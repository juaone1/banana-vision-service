from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.core.config import settings


# Force a valid prefix if the environment value is incorrect
api_prefix = settings.API_V1_STR
if not api_prefix.startswith('/'):
    api_prefix = f"/{api_prefix}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend service for banana disease detection system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - making sure there's no tag or prefix issues
app.include_router(
    auth.router, 
    prefix=api_prefix,
    tags=["auth"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Banana Vision Service"} 