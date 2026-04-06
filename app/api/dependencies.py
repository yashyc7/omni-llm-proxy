from fastapi import Request
from app.services.query_service import QueryService

def get_query_service(request: Request) -> QueryService:
    """Dependency injection for providing the QueryService instance."""
    return request.app.state.query_service
