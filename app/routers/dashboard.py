from fastapi import APIRouter, Query, HTTPException
from typing import Any, Dict, Literal
from app.services.inference_result_service import get_tree_stats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/tree-stats", response_model=Dict[str, Any])
async def tree_stats(
    tree_type: Literal["Healthy", "Infected"] = Query("Healthy", description="Type of tree: Healthy or Infected")
) -> Dict[str, Any]:
    """
    Returns total number of trees (by type) and weekly time series for the past 12 weeks.
    """
    stats = await get_tree_stats(tree_type=tree_type)
    if stats["has_error"]:
        raise HTTPException(status_code=500, detail=stats["error"])
    return stats
