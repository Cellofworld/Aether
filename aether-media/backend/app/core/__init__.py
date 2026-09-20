"""
Core module initialization.

Exports configuration, security utilities, and exceptions.
"""

from app.core.config import settings, get_settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    verify_access_token,
)
from app.core.exceptions import (
    AetherException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    ConflictError,
    MediaNotFoundError,
    TranscodingError,
    ScannerError,
    MetadataError,
    DatabaseError,
)

__all__ = [
    # Config
    "settings",
    "get_settings",
    # Security
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "verify_access_token",
    # Exceptions
    "AetherException",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "MediaNotFoundError",
    "TranscodingError",
    "ScannerError",
    "MetadataError",
    "DatabaseError",
]
