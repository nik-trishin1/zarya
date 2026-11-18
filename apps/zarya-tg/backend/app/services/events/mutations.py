from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.registration import MIN_PARTY_SIZE, Registration, RegistrationStatus
from app.models.user import User
from app.services.access_groups import can_register_for_event, event_allows_plus_one
from app.services.events.queries import (
    _attendance_after_mutation,
    _seat_count_for_event,
    get_event_by_id,
)
from app.services.events.serialization import (
    EventAttendance,
    MOSCOW_TZ,
    _OPEN_RSVP_STATUSES,
    is_event_past,
    validate_party_size,
)
from app.utils.pricing import normalize_event_price


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
        has_open = existing is not None and existing.status in (
            RegistrationStatus.MAYBE.value,
            RegistrationStatus.PENDING.value,
        )
        if not has_open:
            raise ValueError("Event not found")

    if existing and existing.status == RegistrationStatus.ACTIVE.value:
        raise ValueError("Already registered")
    if existing and existing.status == RegistrationStatus.PENDING.value:
        raise ValueError("Already pending")

    if event.max_participants is not None:
        reg_count = await _seat_count_for_event(db, event_id)
        if reg_count + party_size > event.max_participants:
            raise ValueError("Event full")

    requires_approval = bool(getattr(event, "requires_approval", False))
    new_status = (
        RegistrationStatus.PENDING.value if requires_approval else RegistrationStatus.ACTIVE.value
    )

    if existing:
        existing.status = new_status
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
                status=new_status,
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
    if existing and existing.status == RegistrationStatus.PENDING.value:
        raise ValueError("Already pending")

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
            Registration.status.in_(_OPEN_RSVP_STATUSES),
        )
    )
    registration = result.scalar_one_or_none()
    if registration is None:
        raise ValueError("Not registered")

    await clear_maybe_pings(db, registration.registration_id)
    registration.status = RegistrationStatus.CANCELLED.value
    await db.commit()

    return await _attendance_after_mutation(db, event_id, user)


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
    requires_approval: bool = False,
    price_amount_minor: int | None = None,
    price_currency: str | None = None,
) -> Event:
    amount, currency = normalize_event_price(price_amount_minor, price_currency)
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
        requires_approval=requires_approval,
        price_amount_minor=amount,
        price_currency=currency,
        created_by_admin_id=admin_user.user_id,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def update_event(db: AsyncSession, event: Event, **kwargs) -> Event:
    if "price_amount_minor" in kwargs or "price_currency" in kwargs:
        amount, currency = normalize_event_price(
            kwargs.pop("price_amount_minor", None),
            kwargs.pop("price_currency", None),
        )
        event.price_amount_minor = amount
        event.price_currency = currency
    for key, value in kwargs.items():
        if value is not None and hasattr(event, key):
            setattr(event, key, value)
    await db.commit()
    await db.refresh(event)
    return event


async def delete_event(db: AsyncSession, event: Event) -> None:
    await db.delete(event)
    await db.commit()


async def approve_registration(
    db: AsyncSession, event_id: int, applicant_user_id: int
) -> EventAttendance:
    """Admin accepts a pending application. Occupies seats like a normal register."""
    event = await get_event_by_id(db, event_id)
    if event is None:
        raise ValueError("Event not found")

    result = await db.execute(select(User).where(User.user_id == applicant_user_id))
    applicant = result.scalar_one_or_none()
    if applicant is None:
        raise ValueError("User not found")

    reg_result = await db.execute(
        select(Registration).where(
            Registration.user_id == applicant_user_id,
            Registration.event_id == event_id,
        )
    )
    registration = reg_result.scalar_one_or_none()
    if registration is None:
        raise ValueError("Not pending")
    if registration.status == RegistrationStatus.ACTIVE.value:
        raise ValueError("Already registered")
    if registration.status != RegistrationStatus.PENDING.value:
        raise ValueError("Not pending")

    party_size = int(registration.party_size)
    if event.max_participants is not None:
        reg_count = await _seat_count_for_event(db, event_id)
        if reg_count + party_size > event.max_participants:
            raise ValueError("Event full")

    registration.status = RegistrationStatus.ACTIVE.value
    registration.registered_at = datetime.now(MOSCOW_TZ)
    await db.commit()
    return await _attendance_after_mutation(db, event_id, applicant)


async def reject_registration(
    db: AsyncSession, event_id: int, applicant_user_id: int
) -> EventAttendance:
    """Admin declines a pending application."""
    event = await get_event_by_id(db, event_id)
    if event is None:
        raise ValueError("Event not found")

    result = await db.execute(select(User).where(User.user_id == applicant_user_id))
    applicant = result.scalar_one_or_none()
    if applicant is None:
        raise ValueError("User not found")

    reg_result = await db.execute(
        select(Registration).where(
            Registration.user_id == applicant_user_id,
            Registration.event_id == event_id,
        )
    )
    registration = reg_result.scalar_one_or_none()
    if registration is None or registration.status != RegistrationStatus.PENDING.value:
        if registration is not None and registration.status == RegistrationStatus.ACTIVE.value:
            raise ValueError("Already registered")
        raise ValueError("Not pending")

    registration.status = RegistrationStatus.CANCELLED.value
    await db.commit()
    return await _attendance_after_mutation(db, event_id, applicant)
