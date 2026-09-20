"""Metadata models for genres, people, and images."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class Gender(str, enum.Enum):
    """Person gender."""
    UNKNOWN = "unknown"
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"


class Genre(Base):
    """Genre model."""
    
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    tmdb_id = Column(Integer, nullable=True, unique=True)
    
    # Relationships
    media_items = relationship("MediaItem", secondary="media_genres", back_populates="genres")
    
    def __repr__(self) -> str:
        return f"<Genre {self.name}>"


class Person(Base):
    """Person model (actors, directors, etc.)."""
    
    __tablename__ = "people"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    original_name = Column(String(255), nullable=True)
    biography = Column(Text, nullable=True)
    birthday = Column(DateTime, nullable=True)
    deathday = Column(DateTime, nullable=True)
    place_of_birth = Column(String(255), nullable=True)
    gender = Column(SQLEnum(Gender), default=Gender.UNKNOWN, nullable=False)
    tmdb_id = Column(Integer, nullable=True, unique=True)
    profile_path = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    credits = relationship("Credit", back_populates="person", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Person {self.name}>"


class Credit(Base):
    """Credit model linking people to media items."""
    
    __tablename__ = "credits"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    media_id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), nullable=False)
    
    role_type = Column(String(50), nullable=False)  # actor, director, writer, etc.
    character_name = Column(String(255), nullable=True)
    order_index = Column(Integer, nullable=True)  # For billing order
    
    # Relationships
    person = relationship("Person", back_populates="credits")
    media = relationship("MediaItem")
    
    def __repr__(self) -> str:
        return f"<Credit {self.person.name} as {self.role_type}>"


class ImageType(str, enum.Enum):
    """Image types."""
    POSTER = "poster"
    BACKDROP = "backdrop"
    LOGO = "logo"
    THUMBNAIL = "thumbnail"
    PROFILE = "profile"


class MetadataImage(Base):
    """Image associated with media items."""
    
    __tablename__ = "metadata_images"
    
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media_items.id", ondelete="CASCADE"), nullable=False)
    
    image_type = Column(SQLEnum(ImageType), nullable=False)
    path = Column(String(1000), nullable=False)
    url = Column(String(1000), nullable=True)
    
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    aspect_ratio = Column(Float, nullable=True)
    
    language = Column(String(10), nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    
    is_primary = Column(Boolean, default=False, nullable=False)
    tmdb_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    media = relationship("MediaItem", back_populates="images")
    
    def __repr__(self) -> str:
        return f"<MetadataImage {self.image_type}>"
