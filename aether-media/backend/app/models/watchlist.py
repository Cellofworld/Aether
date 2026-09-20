"""
Watchlist model for user media collections.

Allows users to save items for later viewing.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Watchlist(Base):
    """
    Watchlist model for user media collections.

    Allows users to save movies and series they want to watch.

    Attributes:
        id: Unique identifier (UUID)
        user_id: User who owns the watchlist entry
        media_id: Media item in the watchlist
        created_at: When the item was added
    """

    __tablename__ = "watchlists"

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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="watchlist",
    )

    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
        back_populates="watchlist_entries",
    )

    def __repr__(self) -> str:
        """Return string representation of the watchlist entry."""
        return (
            f"<Watchlist(id={self.id}, user_id={self.user_id}, media_id={self.media_id})>"
        )


# Import at end to avoid circular dependencies
from app.models.user import User  # noqa: E402
from app.models.media import MediaItem  # noqa: E402
