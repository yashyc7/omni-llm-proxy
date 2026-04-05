import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import DEFAULT_PROVIDER, PORT
from providers import available_providers, get_provider
from providers.base import BaseProvider

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Active provider (set at startup) ─────────────────────────────────────────
_provider: BaseProvider = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _provider
    name = app.state.provider_name
    logger.info(f"Starting omni-llm-proxy with provider: {name}")
    _provider = get_provider(name)
    await _provider.start()
    yield
    await _provider.stop()


app = FastAPI(
    title="omni-llm-proxy",
    description="Silent multi-LLM browser proxy. One endpoint, any LLM.",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.provider_name = DEFAULT_PROVIDER


# ── Schemas ───────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    provider: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        result = await _provider.query(request.query)
        return QueryResponse(
            response=result,
            provider=app.state.provider_name,
        )
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e  # ← from e


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "provider": app.state.provider_name,
        "available": available_providers(),
    }


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.state.provider_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROVIDER
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)
