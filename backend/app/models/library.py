"""Library models."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text, UniqueConstraint
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class LibraryType(str, enum.Enum):
    """Library types."""
    MOVIES = "movies"
    SERIES = "series"
    ANIME = "anime"
    CARTOONS = "cartoons"
    DOCUMENTARIES = "documentaries"
    MUSIC = "music"
    PHOTOS = "photos"
    OTHER = "other"


class Library(Base):
    """Media library model."""
    
    __tablename__ = "libraries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(SQLEnum(LibraryType), default=LibraryType.MOVIES, nullable=False)
    description = Column(Text, nullable=True)
    
    is_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_scanned_at = Column(DateTime, nullable=True)
    
    # Relationships
    paths = relationship("LibraryPath", back_populates="library", cascade="all, delete-orphan")
    media_items = relationship("MediaItem", back_populates="library", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Library {self.name}>"


class LibraryPath(Base):
    """Path associated with a library."""
    
    __tablename__ = "library_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False)
    path = Column(String(500), nullable=False)
    
    # Relationships
    library = relationship("Library", back_populates="paths")
    
    __table_args__ = (
        UniqueConstraint('library_id', 'path', name='uq_library_path'),
    )
    
    def __repr__(self) -> str:
        return f"<LibraryPath {self.path}>"
