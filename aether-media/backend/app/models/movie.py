"""
Movie model for film-specific metadata.

Extends MediaItem with movie-specific fields.
"""

import uuid
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Movie(Base):
    """
    Movie model for film-specific data.

    Contains additional metadata specific to movies.

    Attributes:
        id: Unique identifier (UUID)
        media_id: Reference to parent MediaItem
        tmdb_id: TMDB movie ID
        runtime: Runtime in minutes
        tagline: Movie tagline
        genres: List of genres (JSON)
        release_date: Theatrical release date
        budget: Production budget
        revenue: Box office revenue
        status: Release status
    """

    __tablename__ = "movies"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("media_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    tmdb_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    runtime: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    tagline: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    genres: Mapped[Optional[list[dict]]] = mapped_column(
        JSON,
        default=list,
        nullable=True,
    )

    release_date: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    budget: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    revenue: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # Relationships
    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
        back_populates="movie",
    )

    def __repr__(self) -> str:
        """Return string representation of the movie."""
        return f"<Movie(id={self.id}, media_id={self.media_id})>"


# Import at end to avoid circular dependencies
from app.models.media import MediaItem  # noqa: E402
