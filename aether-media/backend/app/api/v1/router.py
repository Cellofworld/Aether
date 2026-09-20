"""
API v1 Router - Main router that includes all sub-routers.

Centralizes all API v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    libraries,
    media,
    movies,
    series,
    search,
    playback,
    users,
    admin,
)

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(libraries.router, prefix="/libraries", tags=["Libraries"])
api_router.include_router(media.router, prefix="/media", tags=["Media"])
api_router.include_router(movies.router, prefix="/movies", tags=["Movies"])
api_router.include_router(series.router, prefix="/series", tags=["Series"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(playback.router, prefix="/playback", tags=["Playback"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])


@api_router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns basic health status of the API.
    """
    return {"status": "healthy", "version": "v1"}
