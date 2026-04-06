import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import DEFAULT_PROVIDER
from app.core.logger import logger
from app.infrastructure.providers.factory import create_provider
from app.services.query_service import QueryService
from app.api.routers import query, health
from app.api.middleware import global_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    provider_name = getattr(app.state, "provider_name", DEFAULT_PROVIDER)
    logger.info(f"Starting omni-llm-proxy with provider: {provider_name}")
    
    # 1. Instantiate provider via factory
    provider = create_provider(provider_name)
    
    # 2. Instantiate QueryService pointing to the provider
    query_service = QueryService(provider=provider, provider_name=provider_name)
    
    # 3. Mount on app state for dependency injection
    app.state.query_service = query_service
    app.state.provider = provider
    
    # 4. Bootstrap provider connections non-blockingly
    asyncio.create_task(provider.start())
    
    yield
    
    # Clean up
    await provider.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title="omni-llm-proxy",
        description="Silent multi-LLM browser proxy. One endpoint, any LLM.",
        version="2.0.0",
        lifespan=lifespan,
    )

    # Global Exception Handlers
    app.add_exception_handler(Exception, global_exception_handler)

    # Routes
    app.include_router(query.router)
    app.include_router(health.router)

    return app

app = create_app()
