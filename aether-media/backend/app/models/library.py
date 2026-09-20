"""
Library model for organizing media collections.

Represents a collection of media items with shared configuration.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class LibraryType(str, Enum):
    """Library type enumeration."""

    MOVIES = "movies"
    SERIES = "series"
    ANIME = "anime"
    CARTOONS = "cartoons"
    DOCUMENTARIES = "documentaries"
    MUSIC = "music"
    PHOTOS = "photos"
    OTHER = "other"


class Library(Base):
    """
    Library model for organizing media collections.

    A library represents a logical grouping of media items,
    such as "Movies", "TV Shows", "Anime", etc.

    Attributes:
        id: Unique identifier (UUID)
        name: Display name of the library
        type: Type of content in the library
        root_paths: List of root directory paths to scan
        scanner_config: Configuration for the scanner
        is_enabled: Whether the library is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "libraries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    type: Mapped[LibraryType] = mapped_column(
        SQLEnum(LibraryType),
        nullable=False,
        default=LibraryType.MOVIES,
    )

    root_paths: Mapped[Optional[list[str]]] = mapped_column(
        JSON,
        default=list,
        nullable=True,
    )

    scanner_config: Mapped[Optional[dict]] = mapped_column(
        JSON,
        default=dict,
        nullable=True,
    )

    is_enabled: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    media_items: Mapped[list["MediaItem"]] = relationship(
        "MediaItem",
        back_populates="library",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    scan_jobs: Mapped[list["ScanJob"]] = relationship(
        "ScanJob",
        back_populates="library",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the library."""
        return f"<Library(id={self.id}, name={self.name}, type={self.type})>"

    def add_root_path(self, path: str) -> None:
        """Add a root path to the library."""
        if self.root_paths is None:
            self.root_paths = []
        if path not in self.root_paths:
            self.root_paths.append(path)

    def remove_root_path(self, path: str) -> bool:
        """Remove a root path from the library."""
        if self.root_paths and path in self.root_paths:
            self.root_paths.remove(path)
            return True
        return False


# Import at end to avoid circular dependencies
from app.models.media import MediaItem  # noqa: E402
from app.models.scan_job import ScanJob  # noqa: E402
