from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from app.services.user_service import fetch_users_from_supabase, delete_user_from_supabase
from app.schemas.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=dict)
async def get_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None)
):
    result = await fetch_users_from_supabase(limit=limit, offset=offset, search=search)
    if result["error"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"users": result["users"], "total": result["total"]}

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str):
    result = await delete_user_from_supabase(user_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return None
