import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums.blog_status import BlogStatus
from app.enums.blog_type import BlogType

if TYPE_CHECKING:
    from app.models.user import User


class Blog(Base):
    """
    Blog model supporting content versioning.

    Each edit creates a new row (new version) rather than mutating an existing row.
    All versions of the same logical post share the same `blog_group_id`.
    Only one version per group may have `is_active_version=True` at a time,
    which should be enforced at the service layer.
    """

    __tablename__ = "blogs"

    __table_args__ = (
        Index("ix_blogs_blog_group_id", "blog_group_id"),
        Index("ix_blogs_author_id", "author_id"),
        Index("ix_blogs_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    blog_group_id: Mapped[int] = mapped_column(Integer, nullable=False)

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    cover_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[BlogStatus] = mapped_column(
        Enum(BlogStatus, name="blog_status", inherit_schema=True),
        default=BlogStatus.DRAFT,
        server_default=BlogStatus.DRAFT.value,
        nullable=False,
    )

    blog_type: Mapped[BlogType] = mapped_column(
        Enum(BlogType, name="blog_type", inherit_schema=True),
        default=BlogType.ARTICLE,
        server_default=BlogType.ARTICLE.value,
        nullable=False,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    approved_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    is_active_version: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ──────────────────────────────────────────────────────────

    author: Mapped["User"] = relationship(
        "User",
        foreign_keys=[author_id],
        back_populates="blogs_authored",
    )

    approver: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[approved_by],
        back_populates="blogs_approved",
    )


    def __repr__(self) -> str:
        return (
            f"<Blog(id={self.id}, blog_group_id={self.blog_group_id}, "
            f"version={self.version}, status={self.status.value!r})>"
        )
