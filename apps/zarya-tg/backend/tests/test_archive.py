from __future__ import annotations

from datetime import date, time, timedelta

import pytest

from app.database import async_session, engine, Base
from app.models.event import Event
from app.models.registration import Registration, RegistrationStatus
from app.services.events import (
    get_past_events_admin,
    get_past_registered_events,
    get_upcoming_events,
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
async def test_past_registered_events_active_only():
    today = date.today()
    past_active = Event(
        name="Past active",
        description="",
        date=today - timedelta(days=2),
        time=time(19, 0),
        location="Moscow",
    )
    past_maybe = Event(
        name="Past maybe",
        description="",
        date=today - timedelta(days=3),
        time=time(19, 0),
        location="Moscow",
    )
    upcoming_active = Event(
        name="Upcoming active",
        description="",
        date=today + timedelta(days=2),
        time=time(19, 0),
        location="Moscow",
    )

    async with async_session() as db:
        user = await get_or_create_user(db, telegram_id=930_001, username="guest", first_name="Guest")
        db.add_all([past_active, past_maybe, upcoming_active])
        await db.flush()
        db.add_all(
            [
                Registration(user_id=user.user_id, event_id=past_active.event_id),
                Registration(
                    user_id=user.user_id,
                    event_id=past_maybe.event_id,
                    status=RegistrationStatus.MAYBE.value,
                ),
                Registration(user_id=user.user_id, event_id=upcoming_active.event_id),
            ]
        )
        await db.commit()

        archive_rows = await get_past_registered_events(db, user)
        archive_ids = {row.event.event_id for row in archive_rows}
        assert past_active.event_id in archive_ids
        assert past_maybe.event_id not in archive_ids
        assert upcoming_active.event_id not in archive_ids

        upcoming_rows = await get_upcoming_events(db, user=user, registered_only=True)
        upcoming_ids = {row.event.event_id for row in upcoming_rows}
        assert upcoming_active.event_id in upcoming_ids
        assert past_active.event_id not in upcoming_ids


@pytest.mark.asyncio
async def test_past_registered_events_sorted_newest_first():
    today = date.today()
    older = Event(
        name="Older",
        description="",
        date=today - timedelta(days=10),
        time=time(12, 0),
        location="Moscow",
    )
    newer = Event(
        name="Newer",
        description="",
        date=today - timedelta(days=1),
        time=time(18, 0),
        location="Moscow",
    )

    async with async_session() as db:
        user = await get_or_create_user(db, telegram_id=930_002, username="guest2", first_name="Guest")
        db.add_all([older, newer])
        await db.flush()
        db.add_all(
            [
                Registration(user_id=user.user_id, event_id=older.event_id),
                Registration(user_id=user.user_id, event_id=newer.event_id),
            ]
        )
        await db.commit()

        rows = await get_past_registered_events(db, user)
        assert [row.event.event_id for row in rows] == [newer.event_id, older.event_id]


@pytest.mark.asyncio
async def test_admin_past_events_list():
    today = date.today()
    past_event = Event(
        name="Past admin archive",
        description="",
        date=today - timedelta(days=5),
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

        rows = await get_past_events_admin(db)
        listed_ids = {event.event_id for event, _ in rows}
        assert past_event.event_id in listed_ids
        assert upcoming_event.event_id not in listed_ids
