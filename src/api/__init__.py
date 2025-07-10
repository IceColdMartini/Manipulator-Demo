"""
API router configuration
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .social import router as social_router
from .conversations import router as conversations_router

# Create the main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    social_router,
    prefix="/social",
    tags=["Social Media"]
)

api_router.include_router(
    conversations_router,
    prefix="/conversations",
    tags=["Conversations"]
)
