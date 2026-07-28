import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.chat import Chat
    from app.models.user import User


class Message(Base):
    """
    Message model representing a single post within a blog's chat thread.
    """

    __tablename__ = "messages"

    __table_args__ = (
        Index("ix_messages_chat_id", "chat_id"),
        Index("ix_messages_author_id", "author_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────────────────────

    chat: Mapped["Chat"] = relationship(
        "Chat",
        back_populates="messages",
    )

    author: Mapped["User"] = relationship(
        "User",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return (
            f"<Message(id={self.id}, chat_id={self.chat_id}, "
            f"author_id={self.author_id})>"
        )
