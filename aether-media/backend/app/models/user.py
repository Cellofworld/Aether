"""
User model for authentication and authorization.

Represents application users with roles and permissions.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class UserRole(str, Enum):
    """User role enumeration for access control."""

    ADMIN = "admin"
    USER = "user"


class User(Base):
    """
    User model for authentication and authorization.

    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (unique)
        username: User's display name (unique)
        password_hash: Hashed password
        role: User's role (admin or user)
        is_active: Whether the account is active
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
    watch_progress: Mapped[list["WatchProgress"]] = relationship(
        "WatchProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    watchlist: Mapped[list["Watchlist"]] = relationship(
        "Watchlist",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    playback_sessions: Mapped[list["PlaybackSession"]] = relationship(
        "PlaybackSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return string representation of the user."""
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN


# Import at end to avoid circular dependencies
from app.models.watch_progress import WatchProgress  # noqa: E402
from app.models.watchlist import Watchlist  # noqa: E402
from app.models.playback_session import PlaybackSession  # noqa: E402
