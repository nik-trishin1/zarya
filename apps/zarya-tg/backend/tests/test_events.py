from __future__ import annotations

from datetime import date, time, timedelta

import pytest
from sqlalchemy import select

from app.database import async_session, engine, Base
from app.models.event import Event
from app.models.registration import Registration
from app.models.user import User
from app.services.events import get_upcoming_events


@pytest.fixture(autouse=True)
async def ensure_tables():
    import app.models  # noqa: F401
    from app.schema_updates import apply_schema_updates

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(apply_schema_updates)
    yield


@pytest.mark.asyncio
async def test_get_upcoming_events_hides_past_registrations():
    today = date.today()
    past_event = Event(
        name="Past",
        description="",
        date=today - timedelta(days=1),
        time=time(12, 0),
        location="Moscow",
    )
    future_event = Event(
        name="Future",
        description="",
        date=today + timedelta(days=1),
        time=time(12, 0),
        location="Moscow",
    )
    user = User(telegram_id=910_001, username="tester", first_name="Test")

    async with async_session() as db:
        db.add(user)
        await db.flush()
        db.add_all([past_event, future_event])
        await db.flush()
        db.add_all(
            [
                Registration(user_id=user.user_id, event_id=past_event.event_id),
                Registration(user_id=user.user_id, event_id=future_event.event_id),
            ]
        )
        await db.commit()

        result = await db.execute(select(User).where(User.user_id == user.user_id))
        stored_user = result.scalar_one()
        rows = await get_upcoming_events(db, user=stored_user, registered_only=True)

    event_ids = [event.event_id for event, _, _ in rows]
    assert past_event.event_id not in event_ids
    assert future_event.event_id in event_ids
