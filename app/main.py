from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, inference_result, dashboard
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
    allow_origins=["http://localhost:3600","https://banana-vision-app.vercel.app", "https://raspi.bananavisionml.org", "http://192.168.100.91:3600", "http://192.168.127.239:3600"], 
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
app.include_router(
    inference_result.router,
    prefix=api_prefix,
    tags=["inference_results"]
)
app.include_router(
    dashboard.router,
    prefix=api_prefix,
    tags=["dashboard"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Banana Vision Service"} 
