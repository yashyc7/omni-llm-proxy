from app.domain.interfaces import ILlmProvider
from app.core.logger import logger

class QueryService:
    """
    Business logic layer for processing queries.
    Decoupled from FastAPI; depends only on ILlmProvider interface.
    """
    def __init__(self, provider: ILlmProvider, provider_name: str):
        self._provider = provider
        self._provider_name = provider_name

    @property
    def provider_name(self) -> str:
        return self._provider_name

    async def execute_query(self, user_query: str) -> str:
        """Executes a query by passing it to the injected LLM Provider."""
        if not user_query or not user_query.strip():
            raise ValueError("Query cannot be empty.")
            
        try:
            response = await self._provider.query(user_query)
            return response
        except Exception as e:
            logger.error(f"Query Service failed to execute query: {e}")
            raise
