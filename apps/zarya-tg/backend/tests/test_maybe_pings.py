from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.models.event import Event
from app.models.registration import Registration
from app.models.maybe_ping import RegistrationMaybePing
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
    from app.services.events import _seat_count_for_event, mark_maybe, register_user
    from app.services.users import get_or_create_user

    start = datetime.now(MOSCOW_TZ) + timedelta(days=20)
    async with async_session() as db:
        admin = await get_or_create_user(db, telegram_id=940_001, username="maybe_admin", first_name="Admin")
        guest = await get_or_create_user(db, telegram_id=940_002, username="maybe_guest", first_name="Guest")
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

        from app.models.registration import Registration, RegistrationStatus

        reg = (
            await db.execute(
                select(Registration).where(
                    Registration.user_id == guest.user_id,
                    Registration.event_id == event.event_id,
                    Registration.status == RegistrationStatus.MAYBE.value,
                )
            )
        ).scalar_one()
        ping_count = await db.scalar(
            select(func.count())
            .select_from(RegistrationMaybePing)
            .where(RegistrationMaybePing.registration_id == reg.registration_id)
        )
        assert int(ping_count or 0) == 4

        going = await register_user(db, guest, event.event_id, party_size=1)
        assert going.is_registered is True
        assert going.is_maybe is False
        assert await _seat_count_for_event(db, event.event_id) == 1

        left = await db.scalar(
            select(func.count())
            .select_from(RegistrationMaybePing)
            .where(RegistrationMaybePing.registration_id == reg.registration_id)
        )
        assert int(left or 0) == 0


@pytest.mark.asyncio
async def test_clear_maybe_does_not_cancel_active():
    from app.database import async_session
    from app.services.events import clear_maybe_registration, get_event_detail, register_user
    from app.services.users import get_or_create_user

    start = datetime.now(MOSCOW_TZ) + timedelta(days=10)
    async with async_session() as db:
        admin = await get_or_create_user(db, telegram_id=941_001, username="a2", first_name="A")
        guest = await get_or_create_user(db, telegram_id=941_002, username="g2", first_name="G")
        event = Event(
            name="Тест",
            description="d",
            date=start.date(),
            time=start.time().replace(second=0, microsecond=0),
            location="X",
            created_by_admin_id=admin.user_id,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        await register_user(db, guest, event.event_id, party_size=1)
        with pytest.raises(ValueError, match="Not maybe"):
            await clear_maybe_registration(db, guest, event.event_id)

        detail = await get_event_detail(db, event.event_id, guest)
        assert detail is not None
        assert detail.is_registered is True


@pytest.mark.asyncio
async def test_register_from_maybe_without_group_access():
    from app.database import async_session
    from app.models.registration import RegistrationStatus
    from app.services.access_groups import add_user_to_group, get_group_by_slug
    from app.schema_updates import CORE_GROUP_SLUG
    from app.services.events import get_event_detail, mark_maybe, register_user
    from app.services.users import get_or_create_user

    start = datetime.now(MOSCOW_TZ) + timedelta(days=12)
    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        admin = await get_or_create_user(db, telegram_id=942_001, username="ga", first_name="A")
        member = await get_or_create_user(db, telegram_id=942_002, username="gm", first_name="M")
        await add_user_to_group(db, member, group, notify=False)

        event = Event(
            name="Закрытое",
            description="d",
            date=start.date(),
            time=start.time().replace(second=0, microsecond=0),
            location="X",
            audience_group_id=group.group_id,
            created_by_admin_id=admin.user_id,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        await mark_maybe(db, member, event.event_id)
        # Simulate lost membership while maybe row remains
        member_reg = (
            await db.execute(
                select(Registration).where(
                    Registration.user_id == member.user_id,
                    Registration.event_id == event.event_id,
                )
            )
        ).scalar_one()
        assert member_reg.status == RegistrationStatus.MAYBE.value

        from app.models.group_membership import GroupMembership

        await db.delete(
            (
                await db.execute(
                    select(GroupMembership).where(
                        GroupMembership.user_id == member.user_id,
                        GroupMembership.group_id == group.group_id,
                    )
                )
            ).scalar_one()
        )
        await db.commit()

        detail = await get_event_detail(db, event.event_id, member)
        assert detail is not None
        assert detail.is_maybe is True

        going = await register_user(db, member, event.event_id, party_size=1)
        assert going.is_registered is True
        assert going.is_maybe is False
