"""Playback models for watch progress and history."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class WatchProgress(Base):
    """Watch progress tracking for users."""
    
    __tablename__ = "watch_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), nullable=False)
    
    media_type = Column(String(20), nullable=False)  # movie, episode
    
    position = Column(Integer, default=0, nullable=False)  # Position in seconds
    duration = Column(Integer, default=0, nullable=False)  # Total duration in seconds
    
    is_watched = Column(Boolean, default=False, nullable=False)
    watched_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="watch_progress")
    movie = relationship("Movie", back_populates="watch_progress", foreign_keys=[media_id])
    episode = relationship("Episode", back_populates="watch_progress", foreign_keys=[media_id])
    
    def __repr__(self) -> str:
        return f"<WatchProgress User:{self.user_id} Media:{self.media_id}>"


class PlaybackSession(Base):
    """Active playback session."""
    
    __tablename__ = "playback_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), nullable=False)
    
    device_name = Column(String(100), nullable=True)
    device_type = Column(String(50), nullable=True)  # browser, tv, mobile
    client_name = Column(String(100), nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    
    play_method = Column(String(50), nullable=True)  # direct, transcode, remux
    bitrate = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User")
    media = relationship("MediaItem")
    
    def __repr__(self) -> str:
        return f"<PlaybackSession {self.id}>"


class WatchlistItem(Base):
    """User's watchlist items."""
    
    __tablename__ = "watchlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), nullable=False)
    
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="watchlist")
    movie = relationship("Movie", back_populates="watchlist_items", foreign_keys=[media_id])
    series = relationship("Series", back_populates="watchlist_items", foreign_keys=[media_id])
    
    def __repr__(self) -> str:
        return f"<WatchlistItem User:{self.user_id} Media:{self.media_id}>"


class Collection(Base):
    """User-created collections."""
    
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="collections")
    items = relationship("CollectionItem", back_populates="collection", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Collection {self.name}>"


class CollectionItem(Base):
    """Items in a collection."""
    
    __tablename__ = "collection_items"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    media_id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), nullable=False)
    
    position = Column(Integer, default=0, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="items")
    media = relationship("MediaItem")
    
    def __repr__(self) -> str:
        return f"<CollectionItem {self.id}>"
