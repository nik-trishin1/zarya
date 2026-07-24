from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.access_group import AccessGroup
    from app.models.registration import Registration
    from app.models.user import User


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    date: Mapped[date] = mapped_column(Date, nullable=False)
    time: Mapped[time] = mapped_column(Time, nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # Deprecated for ACL — use audience_group_id (ADR-020). Kept for existing rows.
    tier: Mapped[str] = mapped_column(String(50), nullable=False, default="friends")
    audience_group_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("access_groups.group_id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by_admin_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.user_id"), nullable=True
    )
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[Optional["User"]] = relationship(back_populates="created_events")
    audience_group: Mapped[Optional["AccessGroup"]] = relationship(back_populates="events")
    registrations: Mapped[list["Registration"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
