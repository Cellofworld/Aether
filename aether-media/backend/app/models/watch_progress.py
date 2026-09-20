"""
Watch progress model for tracking user playback position.

Enables resume functionality across devices.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    ForeignKey,
    BigInteger,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class WatchProgress(Base):
    """
    Watch progress model for tracking user playback.

    Stores the current playback position for a user watching
    a specific media item (movie or episode).

    Attributes:
        id: Unique identifier (UUID)
        user_id: User who is watching
        media_id: Media item being watched
        episode_id: Episode (for series), nullable for movies
        position_ms: Current position in milliseconds
        duration_ms: Total duration in milliseconds
        watched: Whether the item has been fully watched
        updated_at: Last update timestamp
    """

    __tablename__ = "watch_progress"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("media_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    episode_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    position_ms: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )

    duration_ms: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )

    watched: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="watch_progress",
    )

    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
        back_populates="watch_progress",
    )

    episode: Mapped[Optional["Episode"]] = relationship(
        "Episode",
        back_populates="watch_progress",
    )

    def __repr__(self) -> str:
        """Return string representation of the watch progress."""
        return (
            f"<WatchProgress(id={self.id}, user_id={self.user_id}, "
            f"media_id={self.media_id}, position={self.position_ms}ms)>"
        )

    @property
    def progress_percentage(self) -> float:
        """Calculate progress as percentage."""
        if self.duration_ms == 0:
            return 0.0
        return min(100.0, (self.position_ms / self.duration_ms) * 100)

    @property
    def is_watched(self) -> bool:
        """Check if content is considered watched (>90% or marked as watched)."""
        return self.watched or self.progress_percentage >= 90.0


# Import at end to avoid circular dependencies
from app.models.user import User  # noqa: E402
from app.models.media import MediaItem  # noqa: E402
from app.models.series import Episode  # noqa: E402
from typing import Optional  # noqa: E402
