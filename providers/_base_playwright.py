import logging
from config import PROVIDERS, USER_DATA_DIR, RESPONSE_TIMEOUT, ProviderConfig
from browser import BrowserSession
from providers.base import BaseProvider

logger = logging.getLogger(__name__)


class PlaywrightProvider(BaseProvider):
    _provider_name: str = ""

    def __init__(self):
        self._cfg: ProviderConfig = PROVIDERS[self._provider_name]
        self._session = BrowserSession(
            USER_DATA_DIR.format(provider=self._provider_name)
        )
        self._page = None
        self._system_prompt_done = False

    async def start(self):
        self._page = await self._session.start()
        await self._page.goto(self._cfg.url)
        await self._page.wait_for_load_state("networkidle")
        await self._inject_system_prompt()

    async def query(self, user_query: str) -> str:
        """Execute user query and return response."""
        await self._type_and_submit(user_query)
        return await self._wait_for_response()

    async def stop(self):
        await self._session.stop()

    async def _inject_system_prompt(self):
        """Inject system prompt to initialize the provider."""
        await self._type_and_submit(self._cfg.system_prompt)
        await self._wait_for_response()
        self._system_prompt_done = True
        logger.info(f"✅ {self._provider_name} — system prompt injected")

    async def _type_and_submit(self, text: str):
        """Type text in input field and submit. Uses first tab."""
        # Use the first page from pages list to avoid creating new tabs
        if len(self._page.context.pages) > 0:
            page = self._page.context.pages[0]
        else:
            page = self._page
            
        box = page.locator(self._cfg.input_selector)
        await box.click()
        # Clear the input field (handle both contenteditable and input types)
        await box.evaluate("el => el.innerHTML = ''")
        await box.evaluate("el => el.value = ''")
        await box.type(text, delay=10)
        await box.press("Enter")  # Submit by pressing Enter instead of clicking button

    async def _wait_for_response(self) -> str:
        """
        ChatGPT-specific response waiting.
        Detects the stop button that appears during streaming.
        """
        # Wait for response to start appearing
        await self._page.wait_for_selector(
            self._cfg.response_selector, timeout=RESPONSE_TIMEOUT
        )
        
        # Wait for streaming to complete by checking if stop button disappears
        # (ChatGPT shows a stop button while streaming, hides it when done)
        try:
            await self._page.wait_for_selector(
                "button[aria-label='Stop generating']", timeout=5
            )
            # Stop button found, now wait for it to disappear (streaming complete)
            await self._page.wait_for_selector(
                "button[aria-label='Stop generating']", state="hidden", timeout=RESPONSE_TIMEOUT
            )
        except Exception:
            # If stop button approach doesn't work, fall back to waiting for done_selector
            await self._page.wait_for_selector(
                self._cfg.done_selector, timeout=RESPONSE_TIMEOUT
            )
            await self._page.wait_for_timeout(1000)

        blocks = self._page.locator(self._cfg.response_selector)
        count = await blocks.count()

        if count == 0:
            blocks = self._page.locator("[data-is-last-node]")
            count = await blocks.count()

        if count == 0:
            return ""

        # Wait for response text to stabilize (stop changing)
        last_text = ""
        for _ in range(30):  # Wait up to 30 seconds for text to stop changing
            current_text = (await blocks.nth(count - 1).inner_text()).strip()
            if current_text == last_text and last_text:
                break
            last_text = current_text
            await self._page.wait_for_timeout(1000)

        return last_text
