"""Media models for movies, series, episodes, and video files."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, BigInteger, Text, Enum as SQLEnum, Table, UniqueConstraint
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MediaItemType(str, enum.Enum):
    """Media item types."""
    MOVIE = "movie"
    SERIES = "series"
    SEASON = "season"
    EPISODE = "episode"


class MediaStatus(str, enum.Enum):
    """Media status."""
    PENDING_METADATA = "pending_metadata"
    METADATA_FOUND = "metadata_found"
    NEEDS_REVIEW = "needs_review"
    ERROR = "error"


class MediaItem(Base):
    """Base media item model."""
    
    __tablename__ = "media_items"
    
    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(MediaItemType), nullable=False)
    
    title = Column(String(255), nullable=False, index=True)
    original_title = Column(String(255), nullable=True)
    overview = Column(Text, nullable=True)
    
    release_date = Column(DateTime, nullable=True)
    year = Column(Integer, nullable=True)
    runtime = Column(Integer, nullable=True)  # in minutes
    
    rating = Column(Float, nullable=True)
    votes = Column(BigInteger, nullable=True)
    
    status = Column(SQLEnum(MediaStatus), default=MediaStatus.PENDING_METADATA, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)  # Prevent auto-metadata updates
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    library = relationship("Library", back_populates="media_items")
    video_files = relationship("VideoFile", back_populates="media", cascade="all, delete-orphan")
    genres = relationship("Genre", secondary="media_genres", back_populates="media_items")
    images = relationship("MetadataImage", back_populates="media", cascade="all, delete-orphan")
    
    # Polymorphic identity
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'base'
    }
    
    def __repr__(self) -> str:
        return f"<MediaItem {self.title}>"


class Movie(MediaItem):
    """Movie model."""
    
    __tablename__ = "movies"
    
    id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), primary_key=True)
    tagline = Column(String(255), nullable=True)
    
    # Relationships specific to movies
    watch_progress = relationship("WatchProgress", back_populates="movie", cascade="all, delete-orphan")
    watchlist_items = relationship("WatchlistItem", back_populates="movie", cascade="all, delete-orphan")
    
    __mapper_args__ = {
        'polymorphic_identity': 'movie'
    }
    
    def __repr__(self) -> str:
        return f"<Movie {self.title} ({self.year})>"


class Series(MediaItem):
    """Series/TV Show model."""
    
    __tablename__ = "series"
    
    id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), primary_key=True)
    number_of_seasons = Column(Integer, default=0, nullable=False)
    number_of_episodes = Column(Integer, default=0, nullable=False)
    in_production = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    seasons = relationship("Season", back_populates="series", cascade="all, delete-orphan", order_by="Season.season_number")
    watchlist_items = relationship("WatchlistItem", back_populates="series", cascade="all, delete-orphan")
    
    __mapper_args__ = {
        'polymorphic_identity': 'series'
    }
    
    def __repr__(self) -> str:
        return f"<Series {self.title}>"


class Season(Base):
    """Season model for TV series."""
    
    __tablename__ = "seasons"
    
    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey("series.id", ondelete="CASCADE"), nullable=False)
    season_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    overview = Column(Text, nullable=True)
    air_date = Column(DateTime, nullable=True)
    poster_path = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    series = relationship("Series", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season", cascade="all, delete-orphan", order_by="Episode.episode_number")
    
    __table_args__ = (
        UniqueConstraint('series_id', 'season_number', name='uq_series_season'),
    )
    
    def __repr__(self) -> str:
        return f"<Season {self.series_id} - S{self.season_number}>"


class Episode(MediaItem):
    """Episode model for TV series."""
    
    __tablename__ = "episodes"
    
    id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), primary_key=True)
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    air_date = Column(DateTime, nullable=True)
    runtime = Column(Integer, nullable=True)
    
    # Relationships
    season = relationship("Season", back_populates="episodes")
    watch_progress = relationship("WatchProgress", back_populates="episode", cascade="all, delete-orphan")
    
    __mapper_args__ = {
        'polymorphic_identity': 'episode'
    }
    
    __table_args__ = (
        UniqueConstraint('season_id', 'episode_number', name='uq_season_episode'),
    )
    
    def __repr__(self) -> str:
        return f"<Episode S{self.season.season_number}E{self.episode_number}>"


class VideoFile(Base):
    """Video file model."""
    
    __tablename__ = "video_files"
    
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), nullable=False)
    path = Column(String(1000), nullable=False, unique=True, index=True)
    
    size = Column(BigInteger, nullable=False)
    duration = Column(Float, nullable=False)  # in seconds
    
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    codec = Column(String(50), nullable=True)
    bitrate = Column(Integer, nullable=True)
    framerate = Column(Float, nullable=True)
    container = Column(String(20), nullable=True)
    
    has_hdr = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    media = relationship("MediaItem", back_populates="video_files")
    audio_tracks = relationship("AudioTrack", back_populates="video_file", cascade="all, delete-orphan")
    subtitle_tracks = relationship("SubtitleTrack", back_populates="video_file", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<VideoFile {self.path}>"


class AudioTrack(Base):
    """Audio track model."""
    
    __tablename__ = "audio_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    video_file_id = Column(Integer, ForeignKey("video_files.id", ondelete="CASCADE"), nullable=False)
    index = Column(Integer, nullable=False)
    
    codec = Column(String(50), nullable=True)
    language = Column(String(10), nullable=True)
    channels = Column(Integer, nullable=True)
    bitrate = Column(Integer, nullable=True)
    title = Column(String(255), nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    video_file = relationship("VideoFile", back_populates="audio_tracks")
    
    def __repr__(self) -> str:
        return f"<AudioTrack {self.language} - {self.codec}>"


class SubtitleTrack(Base):
    """Subtitle track model."""
    
    __tablename__ = "subtitle_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    video_file_id = Column(Integer, ForeignKey("video_files.id", ondelete="CASCADE"), nullable=False)
    
    language = Column(String(10), nullable=False)
    path = Column(String(1000), nullable=True)
    is_external = Column(Boolean, default=True, nullable=False)
    is_forced = Column(Boolean, default=False, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    video_file = relationship("VideoFile", back_populates="subtitle_tracks")
    
    def __repr__(self) -> str:
        return f"<SubtitleTrack {self.language}>"


# Association table for many-to-many relationship between MediaItem and Genre
media_genres = Table(
    'media_genres',
    Base.metadata,
    Column('media_id', Integer, ForeignKey('media_items.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)
