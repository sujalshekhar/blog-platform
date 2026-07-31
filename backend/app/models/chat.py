import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.message import Message


class Chat(Base):
    """
    Chat model representing a discussion thread tied to a logical blog post.
    One chat thread exists per unique `blog_group_id`, covering all versions.
    """

    __tablename__ = "chats"

    __table_args__ = (UniqueConstraint("blog_group_id", name="uq_chats_blog_group_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    blog_group_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────────────────────

    # Blog versions sharing this blog_group_id can be queried via:
    # session.query(Blog).filter(Blog.blog_group_id == chat.blog_group_id)

    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, blog_group_id={self.blog_group_id})>"
