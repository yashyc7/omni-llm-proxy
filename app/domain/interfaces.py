from abc import ABC, abstractmethod

class ILlmProvider(ABC):
    """
    Contract for any LLM Provider integrating with the system.
    """
    @abstractmethod
    async def start(self) -> None:
        """Initialize provider resources (e.g. login, browser setup)."""

    @abstractmethod
    async def query(self, user_query: str) -> str:
        """Execute request and return clean response."""

    @abstractmethod
    async def stop(self) -> None:
        """Clean up provider resources safely."""

class IBrowserSession(ABC):
    """
    Interface for browser session management.
    """
    @abstractmethod
    async def start(self):
        """Start and return the core browser page."""

    @abstractmethod
    async def is_page_valid(self) -> bool:
        """Check if current page is alive and functional."""

    @abstractmethod
    async def get_or_restart(self):
        """Return valid page instance or recover via restart."""

    @abstractmethod
    async def stop(self) -> None:
        """Clean up all underlying browser resources."""
