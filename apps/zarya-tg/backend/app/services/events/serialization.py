from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from zoneinfo import ZoneInfo

from app.models.event import Event
from app.models.registration import (
    MAX_PARTY_SIZE_MVP,
    MIN_PARTY_SIZE,
    Registration,
    RegistrationStatus,
)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")

# Current-user RSVP rows that the Mini App can show (not cancelled).
_OPEN_RSVP_STATUSES = (
    RegistrationStatus.ACTIVE.value,
    RegistrationStatus.MAYBE.value,
    RegistrationStatus.PENDING.value,
)


@dataclass(frozen=True)
class EventAttendance:
    event: Event
    registration_count: int
    is_registered: bool
    party_size: int = 0
    is_maybe: bool = False
    is_pending: bool = False


def _flags_from_registration(registration: Registration | None) -> tuple[int, bool, bool]:
    """Return (party_size for going, is_maybe, is_pending)."""
    if registration is None:
        return 0, False, False
    if registration.status == RegistrationStatus.ACTIVE.value:
        return int(registration.party_size), False, False
    if registration.status == RegistrationStatus.MAYBE.value:
        return 0, True, False
    if registration.status == RegistrationStatus.PENDING.value:
        return 0, False, True
    return 0, False, False


def is_event_past(event: Event) -> bool:
    return event.date < date.today()


def is_event_full(event: Event, reg_count: int) -> bool:
    if event.max_participants is None:
        return False
    return reg_count >= event.max_participants


def validate_party_size(party_size: int, *, allows_plus_one: bool = True) -> int:
    if party_size < MIN_PARTY_SIZE:
        raise ValueError("Invalid party size")
    max_allowed = MAX_PARTY_SIZE_MVP if allows_plus_one else MIN_PARTY_SIZE
    if party_size > max_allowed:
        if not allows_plus_one and party_size > MIN_PARTY_SIZE:
            raise ValueError("Plus one not allowed")
        raise ValueError("Invalid party size")
    return party_size
