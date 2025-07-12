"""Database models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, text
from sqlalchemy.dialects.postgresql import ENUM as dbEnum
from sqlalchemy.dialects.postgresql import UUID as dbUuid
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
)


class ProviderType(enum.StrEnum):
    ANILIST = enum.auto()
    MAL = enum.auto()


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        dbUuid(as_uuid=True),
        primary_key=True,
        init=False,
        server_default=text("gen_random_uuid()"),
    )
    provider: Mapped[ProviderType] = mapped_column(
        dbEnum("anilist", "mal", name="ProviderType"),
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),  # arbitrary length tbh; idk if mal/anilist have any limits
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        init=False,
        nullable=False,
        server_default=text("timezone('utc', now())"),
    )
