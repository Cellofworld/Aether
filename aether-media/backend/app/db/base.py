"""
SQLAlchemy declarative base for Aether Media Server.

All models should inherit from Base.
"""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Provides:
    - Async support via AsyncAttrs
    - Declarative base functionality
    - Common metadata
    """

    # Custom naming convention for constraints
    metadata.naming_convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    def __repr__(self) -> str:
        """Provide a nice string representation of model instances."""
        pairs = []
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if value is not None:
                pairs.append(f"{column.name}={value!r}")
        return f"<{self.__class__.__name__}({', '.join(pairs)})>"
