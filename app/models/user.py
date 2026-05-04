from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    preferred_provider: Mapped[Literal["gigachat", "yandexgpt", "ollama"]] = (
        mapped_column(default="gigachat")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )

    conversations: Mapped[list["Conversation"]] = relationship(  # type: ignore
        cascade="all, delete-orphan", back_populates="user"
    )
    notes: Mapped[list["Note"]] = relationship(  # type: ignore
        cascade="all, delete-orphan", back_populates="user"
    )
