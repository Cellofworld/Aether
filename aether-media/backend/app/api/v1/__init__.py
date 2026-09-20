"""
API v1 module initialization.

Exports all v1 API routers.
"""

from app.api.v1.router import api_router

__all__ = ["api_router"]
