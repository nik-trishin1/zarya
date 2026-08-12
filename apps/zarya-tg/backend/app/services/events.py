from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.registration import (
    MAX_PARTY_SIZE_MVP,
    MIN_PARTY_SIZE,
    Registration,
    RegistrationStatus,
)
from app.models.user import User
from app.services.access_groups import (
    can_access_event_detail,
    can_register_for_event,
    event_allows_plus_one,
    is_admin_telegram_id,
    user_group_ids,
)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


@dataclass(frozen=True)
class EventAttendance:
    event: Event
    registration_count: int
    is_registered: bool
    party_size: int = 0
    is_maybe: bool = False


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
                & (Registration.status == RegistrationStatus.ACTIVE.value),
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
    if user:
        reg_result = await db.execute(
            select(Registration.event_id, Registration.party_size, Registration.status).where(
                Registration.user_id == user.user_id,
                Registration.event_id.in_(event_ids),
                Registration.status.in_(
                    [RegistrationStatus.ACTIVE.value, RegistrationStatus.MAYBE.value]
                ),
            )
        )
        for event_id, party_size, status in reg_result.all():
            if status == RegistrationStatus.ACTIVE.value:
                party_by_event[event_id] = int(party_size)
            elif status == RegistrationStatus.MAYBE.value:
                maybe_event_ids.add(event_id)

    return [
        EventAttendance(
            event=event,
            registration_count=counts.get(event.event_id, 0),
            is_registered=event.event_id in party_by_event,
            party_size=party_by_event.get(event.event_id, 0),
            is_maybe=event.event_id in maybe_event_ids,
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
    if user:
        reg_result = await db.execute(
            select(Registration).where(
                Registration.event_id == event_id,
                Registration.user_id == user.user_id,
                Registration.status.in_(
                    [RegistrationStatus.ACTIVE.value, RegistrationStatus.MAYBE.value]
                ),
            )
        )
        registration = reg_result.scalar_one_or_none()
        if registration is not None:
            if registration.status == RegistrationStatus.ACTIVE.value:
                party_size = int(registration.party_size)
            elif registration.status == RegistrationStatus.MAYBE.value:
                is_maybe = True

    return EventAttendance(
        event=event,
        registration_count=reg_count,
        is_registered=party_size > 0,
        party_size=party_size,
        is_maybe=is_maybe,
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
            Registration.status.in_(
                [RegistrationStatus.ACTIVE.value, RegistrationStatus.MAYBE.value]
            ),
        )
    )
    registration = reg_result.scalar_one_or_none()
    party_size = 0
    is_maybe = False
    if registration is not None:
        if registration.status == RegistrationStatus.ACTIVE.value:
            party_size = int(registration.party_size)
        elif registration.status == RegistrationStatus.MAYBE.value:
            is_maybe = True
    return EventAttendance(
        event=event,
        registration_count=reg_count,
        is_registered=party_size > 0,
        party_size=party_size,
        is_maybe=is_maybe,
    )


async def register_user(
    db: AsyncSession,
    user: User,
    event_id: int,
    party_size: int = MIN_PARTY_SIZE,
) -> EventAttendance:
    event = await get_event_by_id(db, event_id)
    if event is None:
        raise ValueError("Event not found")
    party_size = validate_party_size(party_size, allows_plus_one=event_allows_plus_one(event))
    if is_event_past(event):
        raise ValueError("Event past")

    result = await db.execute(
        select(Registration).where(
            Registration.user_id == user.user_id,
            Registration.event_id == event_id,
        )
    )
    existing = result.scalar_one_or_none()

    if not await can_register_for_event(db, event, user):
        has_maybe = existing is not None and existing.status == RegistrationStatus.MAYBE.value
        if not has_maybe:
            raise ValueError("Event not found")

    if existing and existing.status == RegistrationStatus.ACTIVE.value:
        raise ValueError("Already registered")

    if event.max_participants is not None:
        reg_count = await _seat_count_for_event(db, event_id)
        if reg_count + party_size > event.max_participants:
            raise ValueError("Event full")

    if existing:
        existing.status = RegistrationStatus.ACTIVE.value
        existing.registered_at = datetime.now(MOSCOW_TZ)
        existing.party_size = party_size
        from app.services.maybe_pings import clear_maybe_pings

        await clear_maybe_pings(db, existing.registration_id)
    else:
        db.add(
            Registration(
                user_id=user.user_id,
                event_id=event_id,
                party_size=party_size,
            )
        )

    await db.commit()

    return await _attendance_after_mutation(db, event_id, user)


async def mark_maybe(db: AsyncSession, user: User, event_id: int) -> EventAttendance:
    """Set RSVP to maybe and rebuild cascade ping schedule (ADR-022)."""
    from app.services.maybe_pings import rebuild_maybe_ping_schedule

    event = await get_event_by_id(db, event_id)
    if event is None:
        raise ValueError("Event not found")
    if not await can_register_for_event(db, event, user):
        raise ValueError("Event not found")
    if is_event_past(event):
        raise ValueError("Event past")

    result = await db.execute(
        select(Registration).where(
            Registration.user_id == user.user_id,
            Registration.event_id == event_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing and existing.status == RegistrationStatus.ACTIVE.value:
        raise ValueError("Already registered")

    if existing:
        existing.status = RegistrationStatus.MAYBE.value
        existing.registered_at = datetime.now(MOSCOW_TZ)
        registration = existing
    else:
        registration = Registration(
            user_id=user.user_id,
            event_id=event_id,
            status=RegistrationStatus.MAYBE.value,
            party_size=MIN_PARTY_SIZE,
        )
        db.add(registration)
        await db.flush()

    await rebuild_maybe_ping_schedule(db, registration, event)
    await db.commit()
    return await _attendance_after_mutation(db, event_id, user)


async def update_party_size(
    db: AsyncSession,
    user: User,
    event_id: int,
    party_size: int,
) -> EventAttendance:
    event = await get_event_by_id(db, event_id)
    if event is None:
        raise ValueError("Event not found")
    if not await can_register_for_event(db, event, user):
        raise ValueError("Event not found")
    if not event_allows_plus_one(event) and party_size > MIN_PARTY_SIZE:
        raise ValueError("Plus one not allowed")
    party_size = validate_party_size(party_size, allows_plus_one=event_allows_plus_one(event))
    if is_event_past(event):
        raise ValueError("Event past")

    result = await db.execute(
        select(Registration).where(
            Registration.user_id == user.user_id,
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.ACTIVE.value,
        )
    )
    registration = result.scalar_one_or_none()
    if registration is None:
        raise ValueError("Not registered")

    current = int(registration.party_size)
    if party_size == current:
        return await _attendance_after_mutation(db, event_id, user)

    if party_size > current and event.max_participants is not None:
        reg_count = await _seat_count_for_event(db, event_id)
        extra = party_size - current
        if reg_count + extra > event.max_participants:
            raise ValueError("Event full")

    registration.party_size = party_size
    await db.commit()

    return await _attendance_after_mutation(db, event_id, user)


async def clear_maybe_registration(db: AsyncSession, user: User, event_id: int) -> EventAttendance:
    """Clear maybe only — does not cancel an active going RSVP."""
    from app.services.maybe_pings import clear_maybe_pings

    result = await db.execute(
        select(Registration).where(
            Registration.user_id == user.user_id,
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.MAYBE.value,
        )
    )
    registration = result.scalar_one_or_none()
    if registration is None:
        raise ValueError("Not maybe")

    await clear_maybe_pings(db, registration.registration_id)
    registration.status = RegistrationStatus.CANCELLED.value
    await db.commit()
    return await _attendance_after_mutation(db, event_id, user)


async def cancel_registration(db: AsyncSession, user: User, event_id: int) -> EventAttendance:
    from app.services.maybe_pings import clear_maybe_pings

    result = await db.execute(
        select(Registration).where(
            Registration.user_id == user.user_id,
            Registration.event_id == event_id,
            Registration.status.in_(
                [RegistrationStatus.ACTIVE.value, RegistrationStatus.MAYBE.value]
            ),
        )
    )
    registration = result.scalar_one_or_none()
    if registration is None:
        raise ValueError("Not registered")

    await clear_maybe_pings(db, registration.registration_id)
    registration.status = RegistrationStatus.CANCELLED.value
    await db.commit()

    return await _attendance_after_mutation(db, event_id, user)


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


async def create_event(
    db: AsyncSession,
    name: str,
    description: str,
    event_date: date,
    event_time: time,
    location: str,
    cover_image_url: str | None,
    admin_user: User,
    max_participants: int | None = None,
    audience_group_id: int | None = None,
    is_featured: bool = False,
) -> Event:
    event = Event(
        name=name,
        description=description,
        date=event_date,
        time=event_time,
        location=location,
        cover_image_url=cover_image_url,
        max_participants=max_participants,
        audience_group_id=audience_group_id,
        is_featured=is_featured,
        created_by_admin_id=admin_user.user_id,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def update_event(db: AsyncSession, event: Event, **kwargs) -> Event:
    for key, value in kwargs.items():
        if value is not None and hasattr(event, key):
            setattr(event, key, value)
    await db.commit()
    await db.refresh(event)
    return event


async def delete_event(db: AsyncSession, event: Event) -> None:
    await db.delete(event)
    await db.commit()


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
