"""
Pydantic schemas for library-related data.

Provides validation and serialization for library API requests/responses.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.library import LibraryType
from app.models.scan_job import ScanStatus


class LibraryBase(BaseModel):
    """Base schema for library data."""

    name: str = Field(min_length=1, max_length=100)
    type: LibraryType


class LibraryCreate(LibraryBase):
    """Schema for creating a new library."""

    root_paths: List[str] = Field(default_factory=list)
    scanner_config: Optional[dict] = None


class LibraryUpdate(BaseModel):
    """Schema for updating a library."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    root_paths: Optional[List[str]] = None
    scanner_config: Optional[dict] = None
    is_enabled: Optional[bool] = None


class LibraryResponse(LibraryBase):
    """Schema for library response data."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    root_paths: Optional[List[str]] = None
    scanner_config: Optional[dict] = None
    is_enabled: bool
    created_at: datetime
    updated_at: datetime


class LibraryStats(BaseModel):
    """Schema for library statistics."""

    id: str
    name: str
    type: str
    movies: int = 0
    series: int = 0
    seasons: int = 0
    episodes: int = 0
    total_items: int = 0


class ScanJobBase(BaseModel):
    """Base schema for scan job data."""

    library_id: str
    scan_type: str = "full"


class ScanJobCreate(ScanJobBase):
    """Schema for creating a scan job."""

    pass


class ScanJobResponse(BaseModel):
    """Schema for scan job response data."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    library_id: str
    status: ScanStatus
    progress: int
    items_scanned: int
    items_added: int
    items_updated: int
    items_removed: int
    current_file: Optional[str] = None
    error_message: Optional[str] = None
    errors: Optional[List[dict]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
