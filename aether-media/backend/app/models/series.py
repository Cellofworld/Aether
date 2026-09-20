"""
Series, Season, and Episode models for TV show metadata.

Extends MediaItem with series-specific structures.
"""

import uuid
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Series(Base):
    """
    Series model for TV show data.

    Contains metadata specific to TV series.

    Attributes:
        id: Unique identifier (UUID)
        media_id: Reference to parent MediaItem
        tmdb_id: TMDB series ID
        status: Series status (Ended, Returning Series, etc.)
        first_air_date: First episode air date
        last_air_date: Most recent episode air date
        number_of_seasons: Total seasons
        number_of_episodes: Total episodes
        genres: List of genres (JSON)
        networks: Production networks (JSON)
        created_by: Creators (JSON)
    """

    __tablename__ = "series"

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

    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    first_air_date: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    last_air_date: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    number_of_seasons: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    number_of_episodes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    genres: Mapped[Optional[list[dict]]] = mapped_column(
        JSON,
        default=list,
        nullable=True,
    )

    networks: Mapped[Optional[list[dict]]] = mapped_column(
        JSON,
        default=list,
        nullable=True,
    )

    created_by: Mapped[Optional[list[dict]]] = mapped_column(
        JSON,
        default=list,
        nullable=True,
    )

    # Relationships
    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
        back_populates="series",
    )

    seasons: Mapped[list["Season"]] = relationship(
        "Season",
        back_populates="series",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return string representation of the series."""
        return f"<Series(id={self.id}, media_id={self.media_id})>"


class Season(Base):
    """
    Season model for TV season data.

    Represents a single season of a TV series.

    Attributes:
        id: Unique identifier (UUID)
        series_id: Parent series
        media_id: Associated MediaItem
        number: Season number (0 for specials)
        title: Season title
        overview: Season description
        air_date: Season premiere date
        poster_path: Season poster image
        episode_count: Number of episodes
    """

    __tablename__ = "seasons"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    series_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("series.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("media_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    overview: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    air_date: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    poster_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    episode_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Relationships
    series: Mapped["Series"] = relationship(
        "Series",
        back_populates="seasons",
    )

    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
        back_populates="season",
    )

    episodes: Mapped[list["Episode"]] = relationship(
        "Episode",
        back_populates="season",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return string representation of the season."""
        return f"<Season(id={self.id}, series_id={self.series_id}, number={self.number})>"


class Episode(Base):
    """
    Episode model for TV episode data.

    Represents a single episode of a TV series.

    Attributes:
        id: Unique identifier (UUID)
        season_id: Parent season
        media_id: Associated MediaItem
        number: Episode number within season
        absolute_number: Absolute episode number (for anime)
        title: Episode title
        overview: Episode description
        air_date: Episode air date
        runtime: Episode runtime in minutes
        still_path: Episode thumbnail image
        production_code: Production code
        guest_stars: Guest star information (JSON)
    """

    __tablename__ = "episodes"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    season_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("media_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    absolute_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    overview: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    air_date: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    runtime: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    still_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    production_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    guest_stars: Mapped[Optional[list[dict]]] = mapped_column(
        JSON,
        default=list,
        nullable=True,
    )

    # Relationships
    season: Mapped["Season"] = relationship(
        "Season",
        back_populates="episodes",
    )

    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
        back_populates="episode",
    )

    watch_progress: Mapped[list["WatchProgress"]] = relationship(
        "WatchProgress",
        back_populates="episode",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the episode."""
        return f"<Episode(id={self.id}, season_id={self.season_id}, number={self.number})>"


# Import at end to avoid circular dependencies
from app.models.media import MediaItem  # noqa: E402
from app.models.watch_progress import WatchProgress  # noqa: E402
