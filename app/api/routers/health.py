from fastapi import APIRouter, Request
from app.infrastructure.providers.factory import available_providers

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_endpoint(request: Request):
    # Retrieve provider name safely
    query_service = getattr(request.app.state, "query_service", None)
    provider = query_service.provider_name if query_service else "Initializing"

    return {
        "status": "ok",
        "provider": provider,
        "available": available_providers(),
    }
