"""
API v1 routes initialization.

Exports all route modules for the router to include.
"""

from app.api.v1.routes import (
    auth,
    users,
    libraries,
    media,
    movies,
    series,
    search,
    playback,
    admin,
)

__all__ = [
    "auth",
    "users",
    "libraries",
    "media",
    "movies",
    "series",
    "search",
    "playback",
    "admin",
]
