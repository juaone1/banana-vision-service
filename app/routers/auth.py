from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import User, UserRegister, TokenWithRefresh, RefreshTokenRequest
from app.core.config import settings
from app.core.supabase import supabase, supabase_admin
from app.services.auth_service import (
    get_current_user_from_token,
    register_user,
    login_user,
    refresh_user_token,
    logout_user,
)

print(f"Setting up auth router with tokenUrl: '{settings.API_V1_STR}/login'")

# Initialize router without any prefix
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Delegate to service for token validation and user extraction
    return get_current_user_from_token(token)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister) -> User:
    return await register_user(user_data)

@router.post("/login", response_model=TokenWithRefresh)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_user(form_data)

@router.post("/refresh", response_model=TokenWithRefresh)
async def refresh_token(request: Request):
    return await refresh_user_token(request)

@router.post("/logout")
async def logout(request: Request):
    return await logout_user(request)