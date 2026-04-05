import logging

from playwright.async_api import BrowserContext, Page, async_playwright

from config import HEADLESS

logger = logging.getLogger(__name__)

class BrowserSession:
    """One persistent Chrome profile per provider.
    Persistent context = login cookies survive restarts.
    """

    def __init__(self, user_data_dir: str):
        self._user_data_dir = user_data_dir
        self._playwright     = None
        self._context: BrowserContext = None
        self._page: Page     = None

    async def start(self) -> Page:
        self._playwright = await async_playwright().start()
        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=self._user_data_dir,
            headless=HEADLESS,
            args=[
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled",  # avoid bot detection
            ],
        )
        # Use first page if it exists, otherwise create new one
        if len(self._context.pages) > 0:
            self._page = self._context.pages[0]
        else:
            self._page = await self._context.new_page()
        logger.info(f"Browser started | profile: {self._user_data_dir}")
        return self._page

    async def is_page_valid(self) -> bool:
        """Check if the page is still open and valid."""
        if self._page is None:
            return False
        try:
            # Try to execute a simple script to verify page is valid
            await self._page.evaluate("() => true")
            return True
        except Exception:
            return False

    async def get_or_restart(self) -> Page:
        """Get current page if valid, otherwise restart browser."""
        if await self.is_page_valid():
            return self._page
        
        logger.warning("Browser closed detected! Restarting...")
        # Close any remaining context/playwright instances
        await self.stop()
        # Restart
        return await self.start()

    async def stop(self):
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
