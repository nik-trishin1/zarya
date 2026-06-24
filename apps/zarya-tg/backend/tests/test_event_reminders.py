from __future__ import annotations

from datetime import date, datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from app.models.event import Event
from app.services.event_reminders import (
    MOSCOW_TZ,
    build_reminder_message,
    event_is_in_reminder_window,
    get_events_pending_reminder,
    is_scheduler_active_hour,
    process_due_reminders,
)

@pytest.fixture(autouse=True)
async def ensure_tables():
    import app.models  # noqa: F401
    from app.database import engine, Base
    from app.schema_updates import apply_schema_updates

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(apply_schema_updates)
    yield


def _event_at(start: datetime) -> Event:
    local = start.astimezone(MOSCOW_TZ)
    return Event(
        name="Встреча",
        description="",
        date=local.date(),
        time=local.time().replace(second=0, microsecond=0),
        location="Москва",
    )


def test_build_reminder_message():
    event = _event_at(datetime(2026, 6, 28, 19, 0, tzinfo=MOSCOW_TZ))
    message = build_reminder_message(event)
    assert message.startswith("Ждем вас уже завтра!")
    assert "📌 Встреча ·" in message
    assert "📍 Москва" in message
    assert message.endswith("До скорой встречи! ❤️")


def test_event_is_in_reminder_window():
    start = datetime(2026, 6, 28, 19, 0, tzinfo=MOSCOW_TZ)
    event = _event_at(start)
    now = start - timedelta(hours=24)
    assert event_is_in_reminder_window(event, now) is True


def test_event_is_outside_reminder_window():
    start = datetime(2026, 6, 28, 19, 0, tzinfo=MOSCOW_TZ)
    event = _event_at(start)
    now = start - timedelta(hours=12)
    assert event_is_in_reminder_window(event, now) is False


def test_is_scheduler_active_hour():
    active = datetime(2026, 6, 27, 10, 0, tzinfo=MOSCOW_TZ)
    inactive = datetime(2026, 6, 27, 23, 0, tzinfo=MOSCOW_TZ)
    assert is_scheduler_active_hour(active) is True
    assert is_scheduler_active_hour(inactive) is False


@pytest.mark.asyncio
async def test_get_events_pending_reminder():
    from app.database import async_session

    start = datetime.now(MOSCOW_TZ) + timedelta(hours=24)
    event = _event_at(start)
    event.reminder_sent_at = None

    async with async_session() as db:
        db.add(event)
        await db.commit()

        await db.refresh(event)
        pending = await get_events_pending_reminder(db, start - timedelta(hours=24))
        assert any(item.event_id == event.event_id for item in pending)


@pytest.mark.asyncio
async def test_process_due_reminders_marks_event_sent():
    from app.database import async_session
    from app.models.registration import Registration
    from app.models.user import User
    from app.services.users import get_or_create_user

    tick = datetime(2026, 6, 27, 12, 0, tzinfo=MOSCOW_TZ)
    start = tick + timedelta(hours=24)
    event = _event_at(start)
    event.reminder_sent_at = None

    async with async_session() as db:
        user = await get_or_create_user(db, telegram_id=880001, username="guest", first_name="Guest")
        db.add(event)
        await db.flush()
        db.add(Registration(user_id=user.user_id, event_id=event.event_id))
        await db.commit()
        event_id = event.event_id

    bot = MagicMock()
    bot.send_message = AsyncMock()

    from app.services.telegram_delivery import DeliveryOutcome

    with patch(
        "app.services.event_reminders.deliver_bot_message",
        new_callable=AsyncMock,
        return_value=DeliveryOutcome.SENT,
    ):
        processed = await process_due_reminders(bot, now=tick)

    assert processed == 1

    async with async_session() as db:
        from app.services.events import get_event_by_id

        stored = await get_event_by_id(db, event_id)
        assert stored is not None
        assert stored.reminder_sent_at is not None
