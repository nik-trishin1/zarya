from __future__ import annotations

from datetime import date, time, timedelta
from unittest.mock import patch

import pytest

from app.database import async_session, engine, Base
from app.models.event import Event
from app.schema_updates import CORE_GROUP_SLUG
from app.services.access_groups import (
    add_user_to_group,
    build_group_welcome_message,
    event_allows_plus_one,
    event_allows_sharing,
    get_announcement_recipients,
    get_group_by_slug,
)
from app.services.events import get_event_detail, get_upcoming_events, register_user, update_party_size
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
async def test_core_group_seeded():
    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        assert group.name == "Core"


@pytest.mark.asyncio
async def test_seed_core_roster_adds_configured_users():
    async with async_session() as db:
        u1 = await get_or_create_user(db, telegram_id=911_101, username="a", first_name="A")
        u2 = await get_or_create_user(db, telegram_id=911_102, username="b", first_name="B")
        from app.services.access_groups import seed_core_roster

        with patch("app.services.access_groups.send_group_welcome", return_value=True) as welcome:
            added, already, missing = await seed_core_roster(
                db, user_ids=(u1.user_id, u2.user_id, 999_999), notify=True
            )
        assert added == 2
        assert already == 0
        assert missing == 1
        assert welcome.call_count == 2

        with patch("app.services.access_groups.send_group_welcome", return_value=True) as welcome2:
            added2, already2, missing2 = await seed_core_roster(
                db, user_ids=(u1.user_id, u2.user_id), notify=True
            )
        assert added2 == 0
        assert already2 == 2
        assert missing2 == 0
        welcome2.assert_not_called()


@pytest.mark.asyncio
async def test_group_event_hidden_from_non_member():
    today = date.today()
    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        member = await get_or_create_user(db, telegram_id=930_001, username="m", first_name="M")
        outsider = await get_or_create_user(db, telegram_id=930_002, username="o", first_name="O")
        await add_user_to_group(db, member, group, notify=False)

        public = Event(
            name="Public",
            description="",
            date=today + timedelta(days=1),
            time=time(12, 0),
            location="Moscow",
        )
        closed = Event(
            name="Core only",
            description="",
            date=today + timedelta(days=2),
            time=time(12, 0),
            location="Moscow",
            audience_group_id=group.group_id,
        )
        db.add_all([public, closed])
        await db.commit()
        await db.refresh(closed)

        member_list = await get_upcoming_events(db, user=member)
        outsider_list = await get_upcoming_events(db, user=outsider)
        member_ids = {row.event.event_id for row in member_list}
        outsider_ids = {row.event.event_id for row in outsider_list}
        assert public.event_id in member_ids and closed.event_id in member_ids
        assert public.event_id in outsider_ids
        assert closed.event_id not in outsider_ids

        assert await get_event_detail(db, closed.event_id, outsider) is None
        detail = await get_event_detail(db, closed.event_id, member)
        assert detail is not None
        assert event_allows_plus_one(detail.event) is False
        assert event_allows_sharing(detail.event) is False


@pytest.mark.asyncio
async def test_admin_bypass_sees_group_event():
    today = date.today()
    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        admin = await get_or_create_user(db, telegram_id=940_777, username="admin", first_name="Admin")
        closed = Event(
            name="Admin sees",
            description="",
            date=today + timedelta(days=3),
            time=time(18, 0),
            location="Moscow",
            audience_group_id=group.group_id,
        )
        db.add(closed)
        await db.commit()
        await db.refresh(closed)

        with patch("app.services.access_groups.get_settings") as settings:
            settings.return_value.admin_ids = {940_777}
            rows = await get_upcoming_events(db, user=admin)
            assert closed.event_id in {r.event.event_id for r in rows}
            assert await get_event_detail(db, closed.event_id, admin) is not None


@pytest.mark.asyncio
async def test_group_event_rejects_plus_one():
    today = date.today()
    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        member = await get_or_create_user(db, telegram_id=950_001, username="p", first_name="P")
        await add_user_to_group(db, member, group, notify=False)
        event = Event(
            name="No plus one",
            description="",
            date=today + timedelta(days=4),
            time=time(19, 0),
            location="Moscow",
            audience_group_id=group.group_id,
            max_participants=10,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        with pytest.raises(ValueError, match="Plus one not allowed"):
            await register_user(db, member, event.event_id, party_size=2)

        await register_user(db, member, event.event_id, party_size=1)
        with pytest.raises(ValueError, match="Plus one not allowed"):
            await update_party_size(db, member, event.event_id, party_size=2)


@pytest.mark.asyncio
async def test_announcement_recipients_scoped_to_group():
    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        member = await get_or_create_user(db, telegram_id=960_001, username="in", first_name="In")
        await get_or_create_user(db, telegram_id=960_002, username="out", first_name="Out")
        await add_user_to_group(db, member, group, notify=False)

        group_recipients = await get_announcement_recipients(db, group.group_id)
        all_recipients = await get_announcement_recipients(db, None)
        group_ids = {u.telegram_id for u in group_recipients}
        all_ids = {u.telegram_id for u in all_recipients}
        assert 960_001 in group_ids
        assert 960_002 not in group_ids
        assert 960_001 in all_ids and 960_002 in all_ids


def test_welcome_message_mentions_group_name():
    text = build_group_welcome_message("Core")
    assert "Core" in text
    assert "доступны события группы" in text


@pytest.mark.asyncio
async def test_former_member_can_cancel_registration():
    today = date.today()
    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        user = await get_or_create_user(db, telegram_id=980_001, username="ex", first_name="Ex")
        await add_user_to_group(db, user, group, notify=False)
        event = Event(
            name="Leave later",
            description="",
            date=today + timedelta(days=5),
            time=time(20, 0),
            location="Moscow",
            audience_group_id=group.group_id,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        await register_user(db, user, event.event_id, party_size=1)

        from sqlalchemy import delete
        from app.models.group_membership import GroupMembership

        await db.execute(
            delete(GroupMembership).where(
                GroupMembership.user_id == user.user_id,
                GroupMembership.group_id == group.group_id,
            )
        )
        await db.commit()

        # Still visible via active registration / my list
        assert await get_event_detail(db, event.event_id, user) is not None
        my = await get_upcoming_events(db, user=user, registered_only=True)
        assert event.event_id in {row.event.event_id for row in my}

        from app.services.events import cancel_registration

        attendance = await cancel_registration(db, user, event.event_id)
        assert attendance.is_registered is False


@pytest.mark.asyncio
async def test_add_user_to_group_sends_welcome_once():
    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        # Fresh telegram id each run — shared sqlite DB across pytest invocations.
        import time as time_mod

        telegram_id = 970_000_000 + int(time_mod.time() * 1000) % 1_000_000
        user = await get_or_create_user(db, telegram_id=telegram_id, username="w", first_name="W")
        with patch("app.services.access_groups.send_group_welcome", return_value=True) as welcome:
            _, created = await add_user_to_group(db, user, group, notify=True)
            assert created is True
            welcome.assert_called_once()
            _, created_again = await add_user_to_group(db, user, group, notify=True)
            assert created_again is False
            assert welcome.call_count == 1
