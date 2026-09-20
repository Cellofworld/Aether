"""
Scan job model for tracking media scanning operations.

Provides progress tracking and status for background scans.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    String,
    ForeignKey,
    Integer,
    DateTime,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ScanStatus(str, Enum):
    """Scan job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanJob(Base):
    """
    Scan job model for tracking media scanning operations.

    Tracks the progress and results of library scans.

    Attributes:
        id: Unique identifier (UUID)
        library_id: Library being scanned
        status: Current job status
        progress: Progress percentage (0-100)
        items_scanned: Number of items processed
        items_added: Number of new items added
        items_updated: Number of items updated
        items_removed: Number of items removed
        errors: List of errors encountered
        started_at: When the scan started
        completed_at: When the scan finished
    """

    __tablename__ = "scan_jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    library_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("libraries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[ScanStatus] = mapped_column(
        SQLEnum(ScanStatus),
        default=ScanStatus.PENDING,
        nullable=False,
        index=True,
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    items_scanned: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    items_added: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    items_updated: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    items_removed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    errors: Mapped[Optional[list[dict]]] = mapped_column(
        JSON,
        default=list,
        nullable=True,
    )

    current_file: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    library: Mapped["Library"] = relationship(
        "Library",
        back_populates="scan_jobs",
    )

    def __repr__(self) -> str:
        """Return string representation of the scan job."""
        return (
            f"<ScanJob(id={self.id}, library_id={self.library_id}, "
            f"status={self.status}, progress={self.progress}%)>"
        )

    @property
    def is_running(self) -> bool:
        """Check if the scan is currently running."""
        return self.status == ScanStatus.RUNNING

    @property
    def is_complete(self) -> bool:
        """Check if the scan has completed."""
        return self.status == ScanStatus.COMPLETED

    @property
    def has_failed(self) -> bool:
        """Check if the scan has failed."""
        return self.status in (ScanStatus.FAILED, ScanStatus.CANCELLED)


# Import at end to avoid circular dependencies
from app.models.library import Library  # noqa: E402
