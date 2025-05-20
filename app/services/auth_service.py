from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import User, UserRegister, TokenWithRefresh
from app.core.supabase import supabase, supabase_admin
from typing import Optional, Dict, Any
from app.core.logging import get_logger
from fastapi import Response,Request
from fastapi.responses import JSONResponse

logger = get_logger('auth_service')

def get_current_user_from_token(token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = supabase.auth.get_user(token)
        if not user:
            raise credentials_exception
        return User(
            id=user.user.id,
            email=user.user.email,
            full_name=user.user.user_metadata.get("full_name", ""),
            role=user.user.user_metadata.get("role", "farmer"),
            is_active=True,
            created_at=user.user.created_at,
            updated_at=user.user.updated_at
        )
    except Exception:
        raise credentials_exception


async def delete_auth_user(user_id: str) -> None:
    """
    Delete a user from Supabase Auth using admin client
    """
    try:
        # Use admin client to delete the user
        supabase_admin.auth.admin.delete_user(user_id)
        logger.info(f"Successfully deleted auth user: {user_id}")
    except Exception as e:
        logger.error(f"Failed to delete auth user {user_id}: {str(e)}")


async def create_profile(user_id: str, user_data: Dict[str, Any]) -> None:
    """
    Create a profile record in the database
    """
    try:
        data = {
            'id': user_id,
            'email': user_data['email'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'role': user_data['role']
        }
        
        response = supabase_admin.table('profiles').insert(data).execute()
        
        if hasattr(response, 'error') and response.error is not None:
            logger.error(f"Error creating profile: {response.error}")
            await delete_auth_user(user_id)
            raise ValueError(f"Error creating profile: {response.error}")
            
        logger.info(f"Profile created for user: {user_data['email']}")
        
    except Exception as e:
        logger.error(f"Error creating profile in database: {str(e)}")
        await delete_auth_user(user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user profile"
        )


async def register_user(user_data: UserRegister) -> User:
    try:
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "role": user_data.role
                }
            }
        })
        if not auth_response.user:
            logger.error(f"Failed to create user: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        await create_profile(auth_response.user.id,
                        user_data={
                    "email": user_data.email,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "role": user_data.role
                })
        return User(
            id=auth_response.user.id,
            email=auth_response.user.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            is_active=True,
            created_at=auth_response.user.created_at,
            updated_at=auth_response.user.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def login_user(form_data: OAuth2PasswordRequestForm) -> JSONResponse:
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        if not auth_response.session or not auth_response.session.access_token:
            raise ValueError("Authentication failed - no session")
        print("Auth response: ", auth_response)
        response = JSONResponse({
            "message": "Login successful",
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "first_name": auth_response.user.user_metadata.get("first_name", ""),
                "last_name": auth_response.user.user_metadata.get("last_name", ""),
                "role": auth_response.user.user_metadata.get("role", "farmer")
            }
        })
        response.set_cookie(
            key="access_token",
            value=auth_response.session.access_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=3600
        )
        response.set_cookie(
            key="refresh_token",
            value=auth_response.session.refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=604800
        )
        return response
    except Exception as e:
        error_msg = str(e).lower()
        if "email not confirmed" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified. Please check your email to verify your account.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif "invalid login credentials" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

async def logout_user(request: Request) -> JSONResponse:
    access_token = request.cookies.get("access_token")
    if access_token:
        try:
            # Set the access token in the Supabase client for this operation
            supabase.auth.session = {"access_token": access_token}
            supabase.auth.sign_out()
            logger.info("Supabase token revoked for logout")
        except Exception as e:
            logger.error(f"Failed to revoke Supabase token: {str(e)}")
    else:
        logger.warning("No access_token found in cookies during logout")

    response = Response(status_code=204)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    logger.info("User logged out")
    return response

async def refresh_user_token(request: Request) -> JSONResponse:
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token")
        auth_response = supabase.auth.refresh_session(refresh_token)
        response = JSONResponse({
            "message": "Token refreshed",
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "first_name": auth_response.user.user_metadata.get("first_name", ""),
                "last_name": auth_response.user.user_metadata.get("last_name", ""),
                "role": auth_response.user.user_metadata.get("role", "farmer")
            }
        })
        response.set_cookie(
            key="access_token",
            value=auth_response.session.access_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=3600
        )
        response.set_cookie(
            key="refresh_token",
            value=auth_response.session.refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=604800
        )
        return response
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid refresh token" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif "token expired" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Refresh token error: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
