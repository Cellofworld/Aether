"""
Playback session model for tracking active playback sessions.

Provides information about current and historical playback.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    String,
    ForeignKey,
    BigInteger,
    DateTime,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PlayMethod(str, Enum):
    """Playback method enumeration."""

    DIRECT_PLAY = "direct_play"
    DIRECT_STREAM = "direct_stream"  # Remux
    TRANSCODE = "transcode"


class PlaybackSession(Base):
    """
    Playback session model for tracking active playback.

    Records information about media playback sessions.

    Attributes:
        id: Unique identifier (UUID)
        user_id: User who is playing
        media_id: Media item being played
        play_method: How the media is being played
        device_info: Information about the playback device
        client_name: Name of the client application
        started_at: When playback started
        ended_at: When playback ended
        position_ms: Last known position in milliseconds
    """

    __tablename__ = "playback_sessions"

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

    episode_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("episodes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    play_method: Mapped[PlayMethod] = mapped_column(
        SQLEnum(PlayMethod),
        nullable=False,
    )

    device_info: Mapped[Optional[dict]] = mapped_column(
        JSON,
        default=dict,
        nullable=True,
    )

    client_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    device_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    remote_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    position_ms: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="playback_sessions",
    )

    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
    )

    episode: Mapped[Optional["Episode"]] = relationship(
        "Episode",
    )

    def __repr__(self) -> str:
        """Return string representation of the playback session."""
        return (
            f"<PlaybackSession(id={self.id}, user_id={self.user_id}, "
            f"media_id={self.media_id}, play_method={self.play_method})>"
        )

    @property
    def is_active(self) -> bool:
        """Check if the session is currently active."""
        return self.ended_at is None


# Import at end to avoid circular dependencies
from app.models.user import User  # noqa: E402
from app.models.media import MediaItem  # noqa: E402
from app.models.series import Episode  # noqa: E402
