from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import User, UserRegister
from app.core.config import settings
from app.core.supabase import supabase, supabase_admin

print(f"Setting up auth router with tokenUrl: '{settings.API_V1_STR}/login'")

# Initialize router without any prefix
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Verify token with Supabase
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

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister) -> User:
    try:
        # Create user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name,
                    "role": user_data.role
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        return User(
            id=auth_response.user.id,
            email=auth_response.user.email,
            full_name=user_data.full_name,
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

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Login attempt for user: {form_data.username}")
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if not auth_response.session or not auth_response.session.access_token:
            print("Auth response has no session or token")
            raise ValueError("Authentication failed - no session")
        
        print(f"Login successful for {form_data.username}")
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        # Check for common Supabase error messages and provide better responses
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