from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.registration import Registration


class RegistrationMaybePing(Base):
    """Precomputed cascade ping for a maybe RSVP (ADR-022 / T-211)."""

    __tablename__ = "registration_maybe_pings"
    __table_args__ = (
        UniqueConstraint("registration_id", "offset_id", name="uq_maybe_ping_reg_offset"),
    )

    ping_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    registration_id: Mapped[int] = mapped_column(
        ForeignKey("registrations.registration_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    offset_id: Mapped[str] = mapped_column(String(8), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    registration: Mapped["Registration"] = relationship(back_populates="maybe_pings")
