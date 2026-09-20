"""
Media models for representing media items and their files.

Core models for movies, series, episodes, and video files.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    BigInteger,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class MediaType(str, Enum):
    """Media type enumeration."""

    MOVIE = "movie"
    SERIES = "series"
    SEASON = "season"
    EPISODE = "episode"


class MediaItem(Base):
    """
    Base media item model.

    Represents any media entity (movie, series, season, episode).
    Specific types are represented by subclass tables.

    Attributes:
        id: Unique identifier (UUID)
        library_id: Parent library
        type: Type of media item
        title: Display title
        original_title: Original title (if different)
        year: Release year
        metadata: Cached metadata from providers
        poster_path: Path to poster image
        backdrop_path: Path to backdrop image
        tmdb_id: TMDB identifier
        is_locked: Whether metadata is locked from auto-updates
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "media_items"

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

    type: Mapped[MediaType] = mapped_column(
        SQLEnum(MediaType),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    original_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    year: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    metadata: Mapped[Optional[dict]] = mapped_column(
        JSON,
        default=dict,
        nullable=True,
    )

    poster_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    backdrop_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    tmdb_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    is_locked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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
    library: Mapped["Library"] = relationship(
        "Library",
        back_populates="media_items",
    )

    video_files: Mapped[list["VideoFile"]] = relationship(
        "VideoFile",
        back_populates="media_item",
        cascade="all, delete-orphan",
    )

    movie: Mapped[Optional["Movie"]] = relationship(
        "Movie",
        back_populates="media_item",
        uselist=False,
        cascade="all, delete-orphan",
    )

    series: Mapped[Optional["Series"]] = relationship(
        "Series",
        back_populates="media_item",
        uselist=False,
        cascade="all, delete-orphan",
    )

    season: Mapped[Optional["Season"]] = relationship(
        "Season",
        back_populates="media_item",
        uselist=False,
        cascade="all, delete-orphan",
    )

    episode: Mapped[Optional["Episode"]] = relationship(
        "Episode",
        back_populates="media_item",
        uselist=False,
        cascade="all, delete-orphan",
    )

    genres: Mapped[list["MediaGenre"]] = relationship(
        "MediaGenre",
        back_populates="media_item",
        cascade="all, delete-orphan",
    )

    persons: Mapped[list["MediaPerson"]] = relationship(
        "MediaPerson",
        back_populates="media_item",
        cascade="all, delete-orphan",
    )

    watch_progress: Mapped[list["WatchProgress"]] = relationship(
        "WatchProgress",
        back_populates="media_item",
        cascade="all, delete-orphan",
    )

    watchlist_entries: Mapped[list["Watchlist"]] = relationship(
        "Watchlist",
        back_populates="media_item",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the media item."""
        return f"<MediaItem(id={self.id}, title={self.title}, type={self.type})>"


class VideoFile(Base):
    """
    Video file model.

    Represents a physical video file associated with a media item.

    Attributes:
        id: Unique identifier (UUID)
        media_id: Parent media item
        path: Full path to the file
        filename: File name
        size: File size in bytes
        duration: Duration in seconds
        container: Container format (mkv, mp4, etc.)
        video_codec: Video codec (h264, hevc, etc.)
        audio_codec: Audio codec (aac, ac3, etc.)
        resolution: Resolution string (1920x1080)
        width: Video width in pixels
        height: Video height in pixels
        bitrate: Total bitrate in kbps
        framerate: Frame rate
        hdr: Whether HDR is present
        audio_tracks: List of audio track info
        subtitle_tracks: List of subtitle track info
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "video_files"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("media_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    filename: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    size: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )

    duration: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    container: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    video_codec: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    audio_codec: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    resolution: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    bitrate: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    framerate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    hdr: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    audio_tracks: Mapped[Optional[list[dict]]] = mapped_column(
        JSON,
        default=list,
        nullable=True,
    )

    subtitle_tracks: Mapped[Optional[list[dict]]] = mapped_column(
        JSON,
        default=list,
        nullable=True,
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
    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
        back_populates="video_files",
    )

    def __repr__(self) -> str:
        """Return string representation of the video file."""
        return f"<VideoFile(id={self.id}, filename={self.filename})>"


class AudioTrack(Base):
    """Audio track model for detailed audio information."""

    __tablename__ = "audio_tracks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    video_file_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("video_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    language: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )

    codec: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    channels: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    bitrate: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    video_file: Mapped["VideoFile"] = relationship(
        "VideoFile",
        backref="audio_track_list",
    )


class SubtitleTrack(Base):
    """Subtitle track model for detailed subtitle information."""

    __tablename__ = "subtitle_tracks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    video_file_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("video_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    language: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )

    codec: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    is_forced: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    video_file: Mapped["VideoFile"] = relationship(
        "VideoFile",
        backref="subtitle_track_list",
    )


# Import at end to avoid circular dependencies
from app.models.library import Library  # noqa: E402
from app.models.movie import Movie  # noqa: E402
from app.models.series import Series, Season, Episode  # noqa: E402
from app.models.genre import MediaGenre  # noqa: E402
from app.models.person import MediaPerson  # noqa: E402
from app.models.watch_progress import WatchProgress  # noqa: E402
from app.models.watchlist import Watchlist  # noqa: E402
