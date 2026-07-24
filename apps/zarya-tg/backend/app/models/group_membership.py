from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.access_group import AccessGroup
    from app.models.user import User


class GroupMembership(Base):
    __tablename__ = "group_memberships"
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_group_memberships_user_group"),)

    membership_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("access_groups.group_id"), nullable=False, index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="admin")

    user: Mapped["User"] = relationship(back_populates="group_memberships")
    group: Mapped["AccessGroup"] = relationship(back_populates="memberships")
