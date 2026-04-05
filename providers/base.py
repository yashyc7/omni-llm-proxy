from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Contract every LLM provider must fulfill.
    Add a new LLM = subclass this + register in factory.
    """

    @abstractmethod
    async def start(self) -> None:
        """Launch browser, navigate, verify login."""

    @abstractmethod
    async def query(self, user_query: str) -> str:
        """Inject query silently → return clean response."""

    @abstractmethod
    async def stop(self) -> None:
        """Graceful cleanup."""
