from __future__ import annotations

from datetime import date, time, timedelta

import pytest
from sqlalchemy import select

from app.database import async_session, engine, Base
from app.models.event import Event
from app.models.registration import Registration
from app.models.user import User
from app.services.events import (
    get_all_events_admin,
    get_upcoming_events,
    is_event_full,
    is_event_past,
    register_user,
)
from app.services.users import get_or_create_user


@pytest.fixture(autouse=True)
async def ensure_tables():
    import app.models  # noqa: F401
    from app.schema_updates import apply_schema_updates

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(apply_schema_updates)
    yield


@pytest.mark.asyncio
async def test_is_event_past_uses_calendar_date_only():
    today = date.today()
    past = Event(
        name="Past",
        description="",
        date=today - timedelta(days=1),
        time=time(23, 59),
        location="Moscow",
    )
    upcoming = Event(
        name="Today",
        description="",
        date=today,
        time=time(0, 0),
        location="Moscow",
    )
    assert is_event_past(past) is True
    assert is_event_past(upcoming) is False


@pytest.mark.asyncio
async def test_register_user_rejects_past_event():
    today = date.today()
    past_event = Event(
        name="Past",
        description="",
        date=today - timedelta(days=2),
        time=time(12, 0),
        location="Moscow",
    )

    async with async_session() as db:
        user = await get_or_create_user(db, telegram_id=920_001, username="guest", first_name="Guest")
        db.add(past_event)
        await db.commit()
        await db.refresh(past_event)

        result = await db.execute(select(User).where(User.user_id == user.user_id))
        stored_user = result.scalar_one()

        with pytest.raises(ValueError, match="Event past"):
            await register_user(db, stored_user, past_event.event_id)


def test_is_event_full_respects_capacity():
    today = date.today()
    event = Event(
        name="Limited",
        description="",
        date=today + timedelta(days=1),
        time=time(12, 0),
        location="Moscow",
        max_participants=2,
    )
    assert is_event_full(event, 1) is False
    assert is_event_full(event, 2) is True


def test_is_event_full_without_limit():
    event = Event(
        name="Open",
        description="",
        date=date.today(),
        time=time(12, 0),
        location="Moscow",
        max_participants=None,
    )
    assert is_event_full(event, 999) is False


@pytest.mark.asyncio
async def test_my_registrations_hide_past_events():
    today = date.today()
    past_event = Event(
        name="Past meetup",
        description="",
        date=today - timedelta(days=1),
        time=time(19, 0),
        location="Moscow",
    )
    upcoming_event = Event(
        name="Upcoming meetup",
        description="",
        date=today + timedelta(days=2),
        time=time(19, 0),
        location="Moscow",
    )

    async with async_session() as db:
        user = await get_or_create_user(db, telegram_id=920_020, username="guest", first_name="Guest")
        db.add_all([past_event, upcoming_event])
        await db.flush()
        db.add_all(
            [
                Registration(user_id=user.user_id, event_id=past_event.event_id),
                Registration(user_id=user.user_id, event_id=upcoming_event.event_id),
            ]
        )
        await db.commit()
        await db.refresh(upcoming_event)

        rows = await get_upcoming_events(db, user=user, registered_only=True)
        listed_ids = {attendance.event.event_id for attendance in rows}
        assert upcoming_event.event_id in listed_ids
        assert past_event.event_id not in listed_ids


@pytest.mark.asyncio
async def test_admin_event_list_hides_past_events():
    today = date.today()
    past_event = Event(
        name="Past admin",
        description="",
        date=today - timedelta(days=3),
        time=time(12, 0),
        location="Moscow",
    )
    upcoming_event = Event(
        name="Upcoming admin",
        description="",
        date=today + timedelta(days=1),
        time=time(12, 0),
        location="Moscow",
    )

    async with async_session() as db:
        db.add_all([past_event, upcoming_event])
        await db.commit()
        await db.refresh(past_event)
        await db.refresh(upcoming_event)

        rows = await get_all_events_admin(db)
        listed_ids = {event.event_id for event, _ in rows}
        assert upcoming_event.event_id in listed_ids
        assert past_event.event_id not in listed_ids

        # Past event remains stored; it is only hidden from the admin list.
        stored = await db.execute(select(Event).where(Event.event_id == past_event.event_id))
        assert stored.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_register_user_rejects_full_event():
    today = date.today()
    event = Event(
        name="Full",
        description="",
        date=today + timedelta(days=1),
        time=time(12, 0),
        location="Moscow",
        max_participants=1,
    )

    async with async_session() as db:
        host = await get_or_create_user(db, telegram_id=920_010, username="host", first_name="Host")
        guest = await get_or_create_user(db, telegram_id=920_011, username="guest", first_name="Guest")
        db.add(event)
        await db.flush()
        db.add(Registration(user_id=host.user_id, event_id=event.event_id))
        await db.commit()
        await db.refresh(event)

        result = await db.execute(select(User).where(User.user_id == guest.user_id))
        stored_guest = result.scalar_one()

        with pytest.raises(ValueError, match="Event full"):
            await register_user(db, stored_guest, event.event_id)


@pytest.mark.asyncio
async def test_register_plus_one_occupies_two_seats():
    today = date.today()
    event = Event(
        name="Limited",
        description="",
        date=today + timedelta(days=1),
        time=time(18, 0),
        location="Moscow",
        max_participants=3,
    )

    async with async_session() as db:
        user = await get_or_create_user(db, telegram_id=920_030, username="nikita", first_name="Никита")
        db.add(event)
        await db.commit()
        await db.refresh(event)

        attendance = await register_user(db, user, event.event_id, party_size=2)
        assert attendance.party_size == 2
        assert attendance.registration_count == 2
        assert attendance.is_registered is True


@pytest.mark.asyncio
async def test_register_plus_one_rejected_when_one_seat_left():
    today = date.today()
    event = Event(
        name="Almost full",
        description="",
        date=today + timedelta(days=1),
        time=time(18, 0),
        location="Moscow",
        max_participants=2,
    )

    async with async_session() as db:
        host = await get_or_create_user(db, telegram_id=920_031, username="host", first_name="Host")
        guest = await get_or_create_user(db, telegram_id=920_032, username="guest", first_name="Guest")
        db.add(event)
        await db.flush()
        db.add(Registration(user_id=host.user_id, event_id=event.event_id, party_size=1))
        await db.commit()
        await db.refresh(event)

        with pytest.raises(ValueError, match="Event full"):
            await register_user(db, guest, event.event_id, party_size=2)

        attendance = await register_user(db, guest, event.event_id, party_size=1)
        assert attendance.registration_count == 2


@pytest.mark.asyncio
async def test_update_party_size_add_and_remove_plus_one():
    from app.services.events import update_party_size

    today = date.today()
    event = Event(
        name="Party",
        description="",
        date=today + timedelta(days=2),
        time=time(19, 0),
        location="Moscow",
        max_participants=2,
    )

    async with async_session() as db:
        user = await get_or_create_user(db, telegram_id=920_033, username="solo", first_name="Solo")
        other = await get_or_create_user(db, telegram_id=920_034, username="other", first_name="Other")
        db.add(event)
        await db.flush()
        db.add(Registration(user_id=other.user_id, event_id=event.event_id, party_size=1))
        await db.commit()
        await db.refresh(event)

        await register_user(db, user, event.event_id, party_size=1)

        # 2/2 seats taken — cannot add +1
        with pytest.raises(ValueError, match="Event full"):
            await update_party_size(db, user, event.event_id, 2)

        # Free the other seat, then +1 should work
        other_reg = await db.execute(
            select(Registration).where(
                Registration.user_id == other.user_id,
                Registration.event_id == event.event_id,
            )
        )
        other_reg.scalar_one().status = "cancelled"
        await db.commit()

        upgraded = await update_party_size(db, user, event.event_id, 2)
        assert upgraded.party_size == 2
        assert upgraded.registration_count == 2

        downgraded = await update_party_size(db, user, event.event_id, 1)
        assert downgraded.party_size == 1
        assert downgraded.registration_count == 1


@pytest.mark.asyncio
async def test_cancel_registration_frees_plus_one_seats():
    from app.services.events import cancel_registration

    today = date.today()
    event = Event(
        name="Cancel party",
        description="",
        date=today + timedelta(days=1),
        time=time(12, 0),
        location="Moscow",
        max_participants=2,
    )

    async with async_session() as db:
        user = await get_or_create_user(db, telegram_id=920_035, username="pair", first_name="Pair")
        db.add(event)
        await db.commit()
        await db.refresh(event)

        await register_user(db, user, event.event_id, party_size=2)
        cancelled = await cancel_registration(db, user, event.event_id)
        assert cancelled.is_registered is False
        assert cancelled.registration_count == 0
        assert cancelled.party_size == 0

        # Seat freed for another guest
        other = await get_or_create_user(db, telegram_id=920_036, username="next", first_name="Next")
        again = await register_user(db, other, event.event_id, party_size=2)
        assert again.registration_count == 2
