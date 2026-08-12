from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.models.event import Event
from app.services.maybe_pings import (
    MOSCOW_TZ,
    build_maybe_ping_message,
    build_maybe_ping_schedule,
    ping_is_due,
)

@pytest.fixture(autouse=True)
async def ensure_tables():
    import app.models  # noqa: F401
    from app.database import Base, engine
    from app.schema_updates import apply_schema_updates

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(apply_schema_updates)
    yield


def test_build_schedule_far_event_has_four_offsets():
    start = datetime(2026, 9, 1, 19, 0, tzinfo=MOSCOW_TZ)
    now = start - timedelta(days=30)
    entries = build_maybe_ping_schedule(start, now)
    assert [offset for offset, _ in entries] == ["7d", "3d", "2d", "24h"]
    assert entries[0][1] == start - timedelta(days=7)


def test_build_schedule_skips_past_offsets():
    start = datetime(2026, 9, 1, 19, 0, tzinfo=MOSCOW_TZ)
    now = start - timedelta(days=5)
    entries = build_maybe_ping_schedule(start, now)
    assert [offset for offset, _ in entries] == ["3d", "2d", "24h"]


def test_build_schedule_near_event_only_24h():
    start = datetime(2026, 9, 1, 19, 0, tzinfo=MOSCOW_TZ)
    now = start - timedelta(hours=36)
    entries = build_maybe_ping_schedule(start, now)
    assert [offset for offset, _ in entries] == ["24h"]


def test_ping_is_due_window():
    due = datetime(2026, 8, 20, 12, 0, tzinfo=MOSCOW_TZ)
    assert ping_is_due(due, due) is True
    assert ping_is_due(due, due + timedelta(minutes=30)) is True
    assert ping_is_due(due, due + timedelta(hours=2)) is False
    assert ping_is_due(due, due - timedelta(hours=2)) is False


def test_build_maybe_ping_message():
    event = Event(
        name="Ужин",
        description="",
        date=datetime(2026, 9, 1, tzinfo=MOSCOW_TZ).date(),
        time=datetime(2026, 9, 1, 19, 0, tzinfo=MOSCOW_TZ).time(),
        location="Бар",
    )
    message = build_maybe_ping_message(event)
    assert message.startswith("Вы ещё думаете про это событие?")
    assert "📌 Ужин ·" in message
    assert "📍 Бар" in message


@pytest.mark.asyncio
async def test_mark_maybe_does_not_take_seats_and_builds_schedule():
    from app.database import async_session
    from app.models.registration import RegistrationStatus
    from app.models.user import User
    from app.services.events import (
        _seat_count_for_event,
        mark_maybe,
        register_user,
    )
    from app.models.maybe_ping import RegistrationMaybePing
    from sqlalchemy import func, select

    start = datetime.now(MOSCOW_TZ) + timedelta(days=20)
    async with async_session() as db:
        admin = User(telegram_id=9001, username="admin", first_name="Admin")
        guest = User(telegram_id=9002, username="guest", first_name="Guest")
        db.add_all([admin, guest])
        await db.flush()
        event = Event(
            name="Пикник",
            description="d",
            date=start.date(),
            time=start.time().replace(second=0, microsecond=0),
            location="Парк",
            max_participants=2,
            created_by_admin_id=admin.user_id,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        await db.refresh(guest)

        attendance = await mark_maybe(db, guest, event.event_id)
        assert attendance.is_maybe is True
        assert attendance.is_registered is False
        assert await _seat_count_for_event(db, event.event_id) == 0

        ping_count = await db.scalar(
            select(func.count()).select_from(RegistrationMaybePing)
        )
        assert int(ping_count or 0) == 4

        going = await register_user(db, guest, event.event_id, party_size=1)
        assert going.is_registered is True
        assert going.is_maybe is False
        assert await _seat_count_for_event(db, event.event_id) == 1

        left = await db.scalar(select(func.count()).select_from(RegistrationMaybePing))
        assert int(left or 0) == 0
