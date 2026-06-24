from __future__ import annotations

from datetime import date, time, timedelta

import pytest
from sqlalchemy import select

from app.database import async_session, engine, Base
from app.models.event import Event
from app.models.user import User
from app.services.events import is_event_past, register_user
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
