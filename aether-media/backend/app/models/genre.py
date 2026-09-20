"""
Genre model for categorizing media.

Provides genre classification and relationships.
"""

import uuid
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Genre(Base):
    """
    Genre model for media categorization.

    Represents a genre category like "Action", "Drama", etc.

    Attributes:
        id: Unique identifier (UUID)
        name: Genre name
        tmdb_id: TMDB genre ID
    """

    __tablename__ = "genres"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    tmdb_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        unique=True,
    )

    def __repr__(self) -> str:
        """Return string representation of the genre."""
        return f"<Genre(id={self.id}, name={self.name})>"


class MediaGenre(Base):
    """
    Junction table for many-to-many relationship between media and genres.

    Links media items to their genres.

    Attributes:
        media_id: Reference to media item
        genre_id: Reference to genre
    """

    __tablename__ = "media_genres"

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("media_items.id", ondelete="CASCADE"),
        primary_key=True,
    )

    genre_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
        back_populates="genres",
    )

    genre: Mapped["Genre"] = relationship(
        "Genre",
        backref="media_items",
    )

    def __repr__(self) -> str:
        """Return string representation of the media-genre link."""
        return f"<MediaGenre(media_id={self.media_id}, genre_id={self.genre_id})>"


# Import at end to avoid circular dependencies
from app.models.media import MediaItem  # noqa: E402
