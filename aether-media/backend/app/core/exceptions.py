"""
Custom exception classes for Aether Media Server.

Provides consistent error handling across the application.
"""

from typing import Any, Optional


class AetherException(Exception):
    """Base exception class for Aether Media Server."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class AuthenticationError(AetherException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=401, detail=detail)


class AuthorizationError(AetherException):
    """Raised when user lacks permission for an action."""

    def __init__(
        self,
        message: str = "Not authorized to perform this action",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=403, detail=detail)


class NotFoundError(AetherException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=404, detail=detail)


class ValidationError(AetherException):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=422, detail=detail)


class ConflictError(AetherException):
    """Raised when there's a resource conflict."""

    def __init__(
        self,
        message: str = "Resource conflict",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=409, detail=detail)


class MediaNotFoundError(NotFoundError):
    """Raised when a media file is not found."""

    def __init__(
        self,
        message: str = "Media file not found",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, detail=detail)


class TranscodingError(AetherException):
    """Raised when transcoding fails."""

    def __init__(
        self,
        message: str = "Transcoding failed",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=500, detail=detail)


class ScannerError(AetherException):
    """Raised when media scanning fails."""

    def __init__(
        self,
        message: str = "Media scanning failed",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=500, detail=detail)


class MetadataError(AetherException):
    """Raised when metadata fetching fails."""

    def __init__(
        self,
        message: str = "Metadata fetch failed",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=500, detail=detail)


class DatabaseError(AetherException):
    """Raised when database operation fails."""

    def __init__(
        self,
        message: str = "Database error",
        detail: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=500, detail=detail)
