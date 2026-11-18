from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.registration import Registration, RegistrationStatus
from app.models.user import User
from app.services.access_groups import (
    can_access_event_detail,
    is_admin_telegram_id,
    user_group_ids,
)
from app.services.events.serialization import (
    EventAttendance,
    _OPEN_RSVP_STATUSES,
    _flags_from_registration,
)


def _active_seats_expr():
    return func.coalesce(func.sum(Registration.party_size), 0)


async def _seat_count_for_event(db: AsyncSession, event_id: int) -> int:
    count_result = await db.execute(
        select(_active_seats_expr()).where(
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.ACTIVE.value,
        )
    )
    return int(count_result.scalar() or 0)


async def _seat_counts_for_events(db: AsyncSession, event_ids: list[int]) -> dict[int, int]:
    if not event_ids:
        return {}
    count_result = await db.execute(
        select(Registration.event_id, _active_seats_expr())
        .where(
            Registration.event_id.in_(event_ids),
            Registration.status == RegistrationStatus.ACTIVE.value,
        )
        .group_by(Registration.event_id)
    )
    return {event_id: int(seats or 0) for event_id, seats in count_result.all()}


async def _filter_visible_events(
    db: AsyncSession,
    events: list[Event],
    user: User | None,
    *,
    keep_registered: bool = False,
) -> list[Event]:
    if not events:
        return []
    if user is not None and is_admin_telegram_id(user.telegram_id):
        return events

    member_ids: set[int] = set()
    if user is not None:
        member_ids = await user_group_ids(db, user.user_id)

    # registered_only lists already joined on active registration — keep those rows.
    if keep_registered:
        return events

    visible: list[Event] = []
    for event in events:
        if event.audience_group_id is None:
            visible.append(event)
        elif event.audience_group_id in member_ids:
            visible.append(event)
    return visible


async def get_upcoming_events(
    db: AsyncSession,
    user: User | None = None,
    registered_only: bool = False,
) -> list[EventAttendance]:
    today = date.today()

    if registered_only:
        if user is None:
            return []
        query = (
            select(Event)
            .join(
                Registration,
                (Registration.event_id == Event.event_id)
                & (Registration.user_id == user.user_id)
                & (
                    Registration.status.in_(
                        [RegistrationStatus.ACTIVE.value, RegistrationStatus.PENDING.value]
                    )
                ),
            )
            .where(Event.date >= today)
            .order_by(Event.date.asc(), Event.time.asc())
        )
        result = await db.execute(query)
        events = list(result.scalars().all())
    else:
        query = (
            select(Event)
            .where(Event.date >= today)
            .order_by(Event.date.asc(), Event.time.asc())
        )
        result = await db.execute(query)
        events = list(result.scalars().all())

    events = await _filter_visible_events(
        db, events, user, keep_registered=registered_only
    )
    if not events:
        return []

    event_ids = [e.event_id for e in events]
    counts = await _seat_counts_for_events(db, event_ids)

    party_by_event: dict[int, int] = {}
    maybe_event_ids: set[int] = set()
    pending_event_ids: set[int] = set()
    if user:
        reg_result = await db.execute(
            select(Registration.event_id, Registration.party_size, Registration.status).where(
                Registration.user_id == user.user_id,
                Registration.event_id.in_(event_ids),
                Registration.status.in_(_OPEN_RSVP_STATUSES),
            )
        )
        for event_id, party_size, status in reg_result.all():
            if status == RegistrationStatus.ACTIVE.value:
                party_by_event[event_id] = int(party_size)
            elif status == RegistrationStatus.MAYBE.value:
                maybe_event_ids.add(event_id)
            elif status == RegistrationStatus.PENDING.value:
                pending_event_ids.add(event_id)

    return [
        EventAttendance(
            event=event,
            registration_count=counts.get(event.event_id, 0),
            is_registered=event.event_id in party_by_event,
            party_size=party_by_event.get(event.event_id, 0),
            is_maybe=event.event_id in maybe_event_ids,
            is_pending=event.event_id in pending_event_ids,
        )
        for event in events
    ]


async def get_event_by_id(db: AsyncSession, event_id: int) -> Event | None:
    result = await db.execute(select(Event).where(Event.event_id == event_id))
    return result.scalar_one_or_none()


async def get_event_detail(
    db: AsyncSession, event_id: int, user: User | None = None
) -> EventAttendance | None:
    event = await get_event_by_id(db, event_id)
    if event is None:
        return None
    if not await can_access_event_detail(db, event, user):
        return None

    reg_count = await _seat_count_for_event(db, event_id)

    party_size = 0
    is_maybe = False
    is_pending = False
    if user:
        reg_result = await db.execute(
            select(Registration).where(
                Registration.event_id == event_id,
                Registration.user_id == user.user_id,
                Registration.status.in_(_OPEN_RSVP_STATUSES),
            )
        )
        registration = reg_result.scalar_one_or_none()
        party_size, is_maybe, is_pending = _flags_from_registration(registration)

    return EventAttendance(
        event=event,
        registration_count=reg_count,
        is_registered=party_size > 0,
        party_size=party_size,
        is_maybe=is_maybe,
        is_pending=is_pending,
    )


async def _attendance_after_mutation(
    db: AsyncSession, event_id: int, user: User
) -> EventAttendance:
    """Build attendance without ACL hide — used after register/cancel mutations."""
    event = await get_event_by_id(db, event_id)
    assert event is not None
    reg_count = await _seat_count_for_event(db, event_id)
    reg_result = await db.execute(
        select(Registration).where(
            Registration.event_id == event_id,
            Registration.user_id == user.user_id,
            Registration.status.in_(_OPEN_RSVP_STATUSES),
        )
    )
    registration = reg_result.scalar_one_or_none()
    party_size, is_maybe, is_pending = _flags_from_registration(registration)
    return EventAttendance(
        event=event,
        registration_count=reg_count,
        is_registered=party_size > 0,
        party_size=party_size,
        is_maybe=is_maybe,
        is_pending=is_pending,
    )


async def get_past_registered_events(
    db: AsyncSession,
    user: User,
) -> list[EventAttendance]:
    """Past events where the user had active (going) registration — archive only (ADR-023)."""
    today = date.today()
    query = (
        select(Event)
        .join(
            Registration,
            (Registration.event_id == Event.event_id)
            & (Registration.user_id == user.user_id)
            & (Registration.status == RegistrationStatus.ACTIVE.value),
        )
        .where(Event.date < today)
        .order_by(Event.date.desc(), Event.time.desc())
    )
    result = await db.execute(query)
    events = list(result.scalars().all())
    events = await _filter_visible_events(db, events, user, keep_registered=True)
    if not events:
        return []

    event_ids = [e.event_id for e in events]
    counts = await _seat_counts_for_events(db, event_ids)

    party_by_event: dict[int, int] = {}
    reg_result = await db.execute(
        select(Registration.event_id, Registration.party_size).where(
            Registration.user_id == user.user_id,
            Registration.event_id.in_(event_ids),
            Registration.status == RegistrationStatus.ACTIVE.value,
        )
    )
    for event_id, party_size in reg_result.all():
        party_by_event[event_id] = int(party_size)

    return [
        EventAttendance(
            event=event,
            registration_count=counts.get(event.event_id, 0),
            is_registered=True,
            party_size=party_by_event.get(event.event_id, 0),
            is_maybe=False,
            is_pending=False,
        )
        for event in events
    ]


async def get_all_events_admin(db: AsyncSession) -> list[tuple[Event, int]]:
    """Return upcoming events for admin manage UI. Past events stay in DB but are hidden."""
    today = date.today()
    result = await db.execute(
        select(
            Event,
            _active_seats_expr().label("reg_count"),
        )
        .outerjoin(
            Registration,
            (Registration.event_id == Event.event_id)
            & (Registration.status == RegistrationStatus.ACTIVE.value),
        )
        .where(Event.date >= today)
        .group_by(Event.event_id)
        .order_by(Event.date.asc(), Event.time.asc())
    )
    return [(event, int(reg_count or 0)) for event, reg_count in result.all()]


async def get_past_events_admin(db: AsyncSession) -> list[tuple[Event, int]]:
    """Return past events for admin archive UI, newest first (ADR-023)."""
    today = date.today()
    result = await db.execute(
        select(
            Event,
            _active_seats_expr().label("reg_count"),
        )
        .outerjoin(
            Registration,
            (Registration.event_id == Event.event_id)
            & (Registration.status == RegistrationStatus.ACTIVE.value),
        )
        .where(Event.date < today)
        .group_by(Event.event_id)
        .order_by(Event.date.desc(), Event.time.desc())
    )
    return [(event, int(reg_count or 0)) for event, reg_count in result.all()]


async def get_event_registered_users(db: AsyncSession, event_id: int) -> list[User]:
    """Active + maybe registrants for broadcasts and ADR-013 reminders (ADR-022)."""
    result = await db.execute(
        select(User)
        .join(
            Registration,
            (Registration.user_id == User.user_id)
            & (Registration.event_id == event_id)
            & (
                Registration.status.in_(
                    [RegistrationStatus.ACTIVE.value, RegistrationStatus.MAYBE.value]
                )
            ),
        )
        .order_by(Registration.registered_at.asc())
    )
    return list(result.scalars().all())


async def get_event_registration_parties(
    db: AsyncSession, event_id: int
) -> list[tuple[User, int]]:
    """Active registrations with party_size for admin seat-expanded lists."""
    result = await db.execute(
        select(User, Registration.party_size)
        .join(
            Registration,
            (Registration.user_id == User.user_id)
            & (Registration.event_id == event_id)
            & (Registration.status == RegistrationStatus.ACTIVE.value),
        )
        .order_by(Registration.registered_at.asc())
    )
    return [(user, int(party_size)) for user, party_size in result.all()]


async def get_event_maybe_users(db: AsyncSession, event_id: int) -> list[User]:
    """Maybe RSVPs for admin list (after active seat lines)."""
    result = await db.execute(
        select(User)
        .join(
            Registration,
            (Registration.user_id == User.user_id)
            & (Registration.event_id == event_id)
            & (Registration.status == RegistrationStatus.MAYBE.value),
        )
        .order_by(Registration.registered_at.asc())
    )
    return list(result.scalars().all())


async def get_event_pending_users(db: AsyncSession, event_id: int) -> list[tuple[User, int]]:
    """Pending applications for admin list (before confirmed guests)."""
    result = await db.execute(
        select(User, Registration.party_size)
        .join(
            Registration,
            (Registration.user_id == User.user_id)
            & (Registration.event_id == event_id)
            & (Registration.status == RegistrationStatus.PENDING.value),
        )
        .order_by(Registration.registered_at.asc())
    )
    return [(user, int(party_size)) for user, party_size in result.all()]
