from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role: Mapped[Literal["user", "assistant", "tool"]]
    content: Mapped[str | None] = mapped_column(nullable=True)
    tool_name: Mapped[str | None] = mapped_column(nullable=True)
    tool_call_id: Mapped[str | None] = mapped_column(nullable=True)
    tool_arguments: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")  # type: ignore
