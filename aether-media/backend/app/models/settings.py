"""
Settings model for application configuration.

Stores key-value pairs for system settings.
"""

import uuid
from datetime import datetime

from sqlalchemy import String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Setting(Base):
    """
    Settings model for application configuration.

    Stores key-value pairs for various system settings.

    Attributes:
        id: Unique identifier (UUID)
        key: Setting key (unique)
        value: Setting value (JSON)
        updated_at: Last update timestamp
    """

    __tablename__ = "settings"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    value: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return string representation of the setting."""
        return f"<Setting(id={self.id}, key={self.key})>"
