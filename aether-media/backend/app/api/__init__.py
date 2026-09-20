"""
API module initialization.

Exports API routers and dependencies.
"""

from app.api.v1.router import api_router

__all__ = ["api_router"]
