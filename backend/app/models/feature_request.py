import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums.feature_status import FeatureStatus

if TYPE_CHECKING:
    from app.models.user import User


class FeatureRequest(Base):
    """
    FeatureRequest model representing user-submitted feature suggestions.
    """

    __tablename__ = "feature_requests"

    __table_args__ = (
        Index("ix_feature_requests_status", "status"),
        Index("ix_feature_requests_requested_by", "requested_by"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[FeatureStatus] = mapped_column(
        Enum(FeatureStatus, name="feature_status", inherit_schema=True),
        nullable=False,
        default=FeatureStatus.PENDING,
        server_default=FeatureStatus.PENDING.value,
    )

    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    requested_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
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

    requester: Mapped["User"] = relationship(
        "User",
        back_populates="feature_requests",
    )

    def __repr__(self) -> str:
        return (
            f"<FeatureRequest(id={self.id}, title={self.title!r}, "
            f"status={self.status.value!r}, priority={self.priority})>"
        )
