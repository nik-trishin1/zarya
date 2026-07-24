from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.user import User

# MVP product UI allows 1–2; column has no upper bound for a future N-ticket UI (ADR-019).
MAX_PARTY_SIZE_MVP = 2
MIN_PARTY_SIZE = 1


class RegistrationStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event"),
        CheckConstraint("party_size >= 1", name="ck_registrations_party_size_min"),
    )

    registration_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id"), nullable=False, index=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=RegistrationStatus.ACTIVE.value)
    party_size: Mapped[int] = mapped_column(Integer, nullable=False, default=MIN_PARTY_SIZE, server_default="1")

    user: Mapped["User"] = relationship(back_populates="registrations")
    event: Mapped["Event"] = relationship(back_populates="registrations")
