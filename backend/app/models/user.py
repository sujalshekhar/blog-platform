import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums.role import UserRole

if TYPE_CHECKING:
    from app.models.blog import Blog
    from app.models.message import Message
    from app.models.notification import Notification
    from app.models.feature_request import FeatureRequest


class User(Base):
    """
    User model representing registered users on the blog platform.
    Uses modern SQLAlchemy 2.0 style Declarative mapping.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)

    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", inherit_schema=True),
        default=UserRole.USER,
        server_default=UserRole.USER.value,
        nullable=False,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ──────────────────────────────────────────────────────────

    blogs_authored: Mapped[List["Blog"]] = relationship(
        "Blog",
        foreign_keys="Blog.author_id",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    blogs_approved: Mapped[List["Blog"]] = relationship(
        "Blog",
        foreign_keys="Blog.approved_by",
        back_populates="approver",
    )

    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    feature_requests: Mapped[List["FeatureRequest"]] = relationship(
        "FeatureRequest",
        back_populates="requester",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, first_name={self.first_name!r}, "
            f"email={self.email!r}, role={self.role.value})>"
        )
