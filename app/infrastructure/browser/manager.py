from playwright.async_api import BrowserContext, Page, async_playwright
from app.domain.interfaces import IBrowserSession
from app.core.config import HEADLESS
from app.core.logger import logger

class PlaywrightBrowserSession(IBrowserSession):
    """
    Playwright implementation of the Browser Session.
    Maintains a persistent context to preserve cookies.
    """
    def __init__(self, user_data_dir: str):
        self._user_data_dir = user_data_dir
        self._playwright = None
        self._context: BrowserContext = None
        self._page: Page = None

    async def start(self) -> Page:
        self._playwright = await async_playwright().start()
        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=self._user_data_dir,
            headless=HEADLESS,
            args=[
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        if len(self._context.pages) > 0:
            self._page = self._context.pages[0]
        else:
            self._page = await self._context.new_page()
        
        logger.info(f"Browser started | profile: {self._user_data_dir}")
        return self._page

    async def is_page_valid(self) -> bool:
        if self._page is None:
            return False
        try:
            await self._page.evaluate("() => true")
            return True
        except Exception:
            return False

    async def get_or_restart(self) -> Page:
        if await self.is_page_valid():
            return self._page
        
        logger.warning("Browser closed detected! Restarting...")
        await self.stop()
        return await self.start()

    async def stop(self) -> None:
        try:
            if self._context:
                await self._context.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
        finally:
            self._context = None
            self._playwright = None
            self._page = None
