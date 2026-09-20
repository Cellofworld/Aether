"""API routers package."""
from fastapi import APIRouter

from .auth import router as auth_router
from .libraries import router as libraries_router
from .media import router as media_router
from .search import router as search_router
from .playback import router as playback_router
from .admin import router as admin_router

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(libraries_router)  # Already has /libraries prefix
api_router.include_router(media_router)  # Already has /media prefix
api_router.include_router(search_router)  # Already has /search prefix
api_router.include_router(playback_router)  # Already has /playback prefix
api_router.include_router(admin_router)  # Already has /admin prefix

__all__ = ["api_router"]
