from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "api/v1"
    PROJECT_NAME: str = "Banana Vision Service"
    
    # Security (optional since we're using Supabase)
    SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str  # For admin operations

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()