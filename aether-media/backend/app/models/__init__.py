"""
Database models for Aether Media Server.

This module exports all model classes for use throughout the application.
"""

# Import all models to ensure they're registered with SQLAlchemy
from app.models.user import User, UserRole
from app.models.library import Library, LibraryType
from app.models.media import (
    MediaItem,
    MediaType,
    VideoFile,
    AudioTrack,
    SubtitleTrack,
)
from app.models.movie import Movie
from app.models.series import Series, Season, Episode
from app.models.watch_progress import WatchProgress
from app.models.genre import Genre, MediaGenre
from app.models.person import Person, MediaPerson
from app.models.watchlist import Watchlist
from app.models.settings import Setting
from app.models.scan_job import ScanJob, ScanStatus
from app.models.playback_session import PlaybackSession, PlayMethod

__all__ = [
    # User
    "User",
    "UserRole",
    # Library
    "Library",
    "LibraryType",
    # Media
    "MediaItem",
    "MediaType",
    "VideoFile",
    "AudioTrack",
    "SubtitleTrack",
    # Movie
    "Movie",
    # Series
    "Series",
    "Season",
    "Episode",
    # Watch Progress
    "WatchProgress",
    # Genre
    "Genre",
    "MediaGenre",
    # Person
    "Person",
    "MediaPerson",
    # Watchlist
    "Watchlist",
    # Settings
    "Setting",
    # Scan Job
    "ScanJob",
    "ScanStatus",
    # Playback Session
    "PlaybackSession",
    "PlayMethod",
]
