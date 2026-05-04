from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )

    user: Mapped["User"] = relationship(back_populates="conversations")  # type: ignore
    messages: Mapped[list["Message"]] = relationship(  # type: ignore
        cascade="all, delete-orphan", back_populates="conversation"
    )
