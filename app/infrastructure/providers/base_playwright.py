import asyncio
from app.domain.interfaces import ILlmProvider, IBrowserSession
from app.domain.schemas import ProviderConfig
from app.core.config import RESPONSE_TIMEOUT
from app.core.logger import logger

class BasePlaywrightProvider(ILlmProvider):
    def __init__(self, name: str, config: ProviderConfig, session: IBrowserSession):
        self._name = name
        self._cfg = config
        self._session = session
        self._page = None
        self._system_prompt_done = False
        
        # Request queueing items
        self._queue = asyncio.Queue()
        self._worker_task = None

    async def start(self) -> None:
        try:
            await self._ensure_page()
        except Exception as e:
            logger.error(f"Error during initial page setup for {self._name}: {e}")
            
        self._worker_task = asyncio.create_task(self._worker())

    async def _worker(self):
        """Background task that sequentially processes queued queries."""
        while True:
            item = await self._queue.get()
            if item is None:
                self._queue.task_done()
                break
                
            user_query, future = item
            try:
                await self._ensure_page()
                initial_count = await self._get_response_count()
                
                await self._type_and_submit(user_query)
                response = await self._wait_for_response(initial_count)
                
                if not future.done():
                    future.set_result(response)
            except Exception as e:
                logger.error(f"Error processing query in {self._name}: {e}")
                if not future.done():
                    future.set_exception(e)
            finally:
                self._queue.task_done()

    async def _ensure_page(self):
        if await self._session.is_page_valid():
            return
            
        logger.warning(f"Re-initializing browser page for {self._name}")
        self._page = await self._session.get_or_restart()
        await self._page.goto(self._cfg.url)
        try:
            await self._page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        self._system_prompt_done = False
        await self._inject_system_prompt()

    async def _get_response_count(self) -> int:
        blocks = self._page.locator(self._cfg.response_selector)
        count = await blocks.count()
        if count == 0:
            blocks = self._page.locator("[data-is-last-node]")
            count = await blocks.count()
        return count

    async def query(self, user_query: str) -> str:
        """Enqueues the query and returns a future to be resolved by the worker."""
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        await self._queue.put((user_query, future))
        return await future

    async def stop(self) -> None:
        if self._worker_task:
            await self._queue.put(None)
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        await self._session.stop()

    async def _inject_system_prompt(self):
        initial_count = await self._get_response_count()
        await self._type_and_submit(self._cfg.system_prompt)
        await self._wait_for_response(initial_count)
        self._system_prompt_done = True
        logger.info(f"✅ {self._name} — system prompt injected")

    async def _type_and_submit(self, text: str):
        if len(self._page.context.pages) > 0:
            page = self._page.context.pages[0]
        else:
            page = self._page
            
        box = page.locator(self._cfg.input_selector)
        await box.click()
        await box.evaluate("el => el.innerHTML = ''")
        await box.evaluate("el => el.value = ''")
        await box.type(text, delay=10)
        await box.press("Enter")

    async def _wait_for_response(self, initial_count: int = 0) -> str:
        blocks = self._page.locator(self._cfg.response_selector)
        
        found_new_block = False
        for _ in range(int(RESPONSE_TIMEOUT / 500)):
            count = await blocks.count()
            if count == 0:
                fallback_blocks = self._page.locator("[data-is-last-node]")
                count = await fallback_blocks.count()
                if count > initial_count:
                    blocks = fallback_blocks
                    found_new_block = True
                    break
            elif count > initial_count:
                found_new_block = True
                break
            await self._page.wait_for_timeout(500)

        if not found_new_block:
            raise TimeoutError(f"Provider {self._name} did not generate a new response block within timeout.")

        try:
            await self._page.wait_for_selector(
                "button[aria-label='Stop generating']", timeout=5000
            )
            await self._page.wait_for_selector(
                "button[aria-label='Stop generating']", state="hidden", timeout=RESPONSE_TIMEOUT
            )
        except Exception:
            try:
                await self._page.wait_for_selector(
                    self._cfg.done_selector, timeout=RESPONSE_TIMEOUT
                )
            except Exception:
                pass
            await self._page.wait_for_timeout(1000)

        count = await blocks.count()
        if count <= initial_count:
            raise TimeoutError(f"Provider {self._name} did not generate a new response block after waiting.")

        last_text = ""
        for _ in range(30):
            current_text = (await blocks.nth(count - 1).inner_text()).strip()
            if current_text == last_text and last_text:
                break
            last_text = current_text
            await self._page.wait_for_timeout(1000)

        return last_text
