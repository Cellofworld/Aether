"""
Person model for cast and crew information.

Stores actor, director, writer, and other personnel data.
"""

import uuid
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Person(Base):
    """
    Person model for cast and crew members.

    Represents actors, directors, writers, and other personnel.

    Attributes:
        id: Unique identifier (UUID)
        name: Full name
        tmdb_id: TMDB person ID
        profile_path: Profile image path
        biography: Biographical text
        birth_date: Date of birth
        death_date: Date of death (if deceased)
        place_of_birth: Birthplace
        known_for_department: Primary department
    """

    __tablename__ = "persons"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    tmdb_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        unique=True,
        index=True,
    )

    profile_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    biography: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    birth_date: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    death_date: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    place_of_birth: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    known_for_department: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    popularity: Mapped[Optional[float]] = mapped_column(
        default=0.0,
    )

    def __repr__(self) -> str:
        """Return string representation of the person."""
        return f"<Person(id={self.id}, name={self.name})>"


class MediaPerson(Base):
    """
    Junction table for many-to-many relationship between media and persons.

    Links media items to cast and crew members with role information.

    Attributes:
        media_id: Reference to media item
        person_id: Reference to person
        role: Role type (actor, director, writer, etc.)
        character: Character name (for actors)
        order: Display order (for cast)
        department: Department (for crew)
        job: Job title (for crew)
    """

    __tablename__ = "media_persons"

    media_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("media_items.id", ondelete="CASCADE"),
        primary_key=True,
    )

    person_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("persons.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    character: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    order: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    job: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Relationships
    media_item: Mapped["MediaItem"] = relationship(
        "MediaItem",
        back_populates="persons",
    )

    person: Mapped["Person"] = relationship(
        "Person",
        backref="media_roles",
    )

    def __repr__(self) -> str:
        """Return string representation of the media-person link."""
        return (
            f"<MediaPerson(media_id={self.media_id}, person_id={self.person_id}, "
            f"role={self.role})>"
        )


# Import at end to avoid circular dependencies
from app.models.media import MediaItem  # noqa: E402
