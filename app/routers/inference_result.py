from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.inference_result import InferenceResultOut
from app.services.inference_result_service import get_inference_results

router = APIRouter(prefix="/inference-results", tags=["inference_results"])

from fastapi import Query
from typing import Any, Dict

@router.get("/", response_model=Dict[str, Any])
async def list_inference_results(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
) -> Dict[str, Any]:
    """
    List inference results with pagination. Pass ?page=1&limit=20. Offset is handled automatically.
    """
    offset = (page - 1) * limit
    result = await get_inference_results(limit=limit, offset=offset)
    if result["has_error"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
