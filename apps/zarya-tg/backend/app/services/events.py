from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.registration import Registration, RegistrationStatus
from app.models.user import User

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def is_event_past(event: Event) -> bool:
    return event.date < date.today()


def is_event_full(event: Event, reg_count: int) -> bool:
    if event.max_participants is None:
        return False
    return reg_count >= event.max_participants


async def get_upcoming_events(
    db: AsyncSession,
    user: User | None = None,
    registered_only: bool = False,
) -> list[tuple[Event, int, bool]]:
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

    if not events:
        return []

    event_ids = [e.event_id for e in events]
    count_result = await db.execute(
        select(Registration.event_id, func.count(Registration.registration_id))
        .where(
            Registration.event_id.in_(event_ids),
            Registration.status == RegistrationStatus.ACTIVE.value,
        )
        .group_by(Registration.event_id)
    )
    counts = dict(count_result.all())

    registered_event_ids: set[int] = set()
    if user:
        reg_result = await db.execute(
            select(Registration.event_id).where(
                Registration.user_id == user.user_id,
                Registration.event_id.in_(event_ids),
                Registration.status == RegistrationStatus.ACTIVE.value,
            )
        )
        registered_event_ids = set(reg_result.scalars().all())

    return [
        (event, counts.get(event.event_id, 0), event.event_id in registered_event_ids)
        for event in events
    ]


async def get_event_by_id(db: AsyncSession, event_id: int) -> Event | None:
    result = await db.execute(select(Event).where(Event.event_id == event_id))
    return result.scalar_one_or_none()


async def get_event_detail(
    db: AsyncSession, event_id: int, user: User | None = None
) -> tuple[Event, int, bool] | None:
    event = await get_event_by_id(db, event_id)
    if event is None:
        return None

    count_result = await db.execute(
        select(func.count(Registration.registration_id)).where(
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.ACTIVE.value,
        )
    )
    reg_count = count_result.scalar() or 0

    is_registered = False
    if user:
        reg_result = await db.execute(
            select(Registration).where(
                Registration.event_id == event_id,
                Registration.user_id == user.user_id,
                Registration.status == RegistrationStatus.ACTIVE.value,
            )
        )
        is_registered = reg_result.scalar_one_or_none() is not None

    return event, reg_count, is_registered


async def register_user(db: AsyncSession, user: User, event_id: int) -> tuple[Event, int, bool]:
    event = await get_event_by_id(db, event_id)
    if event is None:
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

    if event.max_participants is not None:
        count_result = await db.execute(
            select(func.count(Registration.registration_id)).where(
                Registration.event_id == event_id,
                Registration.status == RegistrationStatus.ACTIVE.value,
            )
        )
        reg_count = count_result.scalar() or 0
        if reg_count >= event.max_participants:
            raise ValueError("Event full")

    if existing:
        existing.status = RegistrationStatus.ACTIVE.value
        existing.registered_at = datetime.now(MOSCOW_TZ)
    else:
        db.add(Registration(user_id=user.user_id, event_id=event_id))

    await db.commit()

    detail = await get_event_detail(db, event_id, user)
    assert detail is not None
    return detail


async def cancel_registration(db: AsyncSession, user: User, event_id: int) -> tuple[Event, int, bool]:
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

    registration.status = RegistrationStatus.CANCELLED.value
    await db.commit()

    detail = await get_event_detail(db, event_id, user)
    assert detail is not None
    return detail


async def get_all_events_admin(db: AsyncSession) -> list[tuple[Event, int]]:
    result = await db.execute(
        select(
            Event,
            func.count(Registration.registration_id).label("reg_count"),
        )
        .outerjoin(
            Registration,
            (Registration.event_id == Event.event_id)
            & (Registration.status == RegistrationStatus.ACTIVE.value),
        )
        .group_by(Event.event_id)
        .order_by(Event.date.desc(), Event.time.desc())
    )
    return [(event, reg_count) for event, reg_count in result.all()]


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
) -> Event:
    event = Event(
        name=name,
        description=description,
        date=event_date,
        time=event_time,
        location=location,
        cover_image_url=cover_image_url,
        max_participants=max_participants,
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
    result = await db.execute(
        select(User)
        .join(
            Registration,
            (Registration.user_id == User.user_id)
            & (Registration.event_id == event_id)
            & (Registration.status == RegistrationStatus.ACTIVE.value),
        )
        .order_by(Registration.registered_at.asc())
    )
    return list(result.scalars().all())
