from fastapi import APIRouter, Depends, HTTPException
from app.domain.schemas import QueryRequest, QueryResponse
from app.services.query_service import QueryService
from app.api.dependencies import get_query_service

router = APIRouter(tags=["query"])

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(
    request: QueryRequest, 
    service: QueryService = Depends(get_query_service)
):
    try:
        result = await service.execute_query(request.query)
        return QueryResponse(
            response=result,
            provider=service.provider_name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
