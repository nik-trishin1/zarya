from __future__ import annotations

from datetime import date, time, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import async_session, engine, Base
from app.main import app
from app.models.event import Event
from app.schema_updates import CORE_GROUP_SLUG
from app.services.access_groups import add_user_to_group, get_group_by_slug
from app.services.events import create_event, get_upcoming_events, update_event
from app.services.users import get_or_create_user


@pytest.fixture(autouse=True)
async def ensure_tables():
    import app.models  # noqa: F401
    from app.schema_updates import apply_schema_updates

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(apply_schema_updates)
    yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_event_defaults_is_featured_false():
    async with async_session() as db:
        admin = await get_or_create_user(db, telegram_id=940_001, username="a", first_name="A")
        event = await create_event(
            db,
            name="Plain",
            description="",
            event_date=date.today() + timedelta(days=3),
            event_time=time(19, 0),
            location="Moscow",
            cover_image_url=None,
            admin_user=admin,
        )
        assert event.is_featured is False


@pytest.mark.asyncio
async def test_create_and_update_is_featured():
    async with async_session() as db:
        admin = await get_or_create_user(db, telegram_id=940_002, username="b", first_name="B")
        event = await create_event(
            db,
            name="Featured",
            description="",
            event_date=date.today() + timedelta(days=4),
            event_time=time(20, 0),
            location="Moscow",
            cover_image_url=None,
            admin_user=admin,
            is_featured=True,
        )
        assert event.is_featured is True

        updated = await update_event(db, event, is_featured=False)
        assert updated.is_featured is False

        updated = await update_event(db, event, is_featured=True)
        assert updated.is_featured is True


@pytest.mark.asyncio
async def test_api_returns_is_featured(client: AsyncClient):
    async with async_session() as db:
        event = Event(
            name="API featured",
            description="",
            date=date.today() + timedelta(days=5),
            time=time(18, 0),
            location="Moscow",
            is_featured=True,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        event_id = event.event_id

    response = await client.get(f"/api/events/{event_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_featured"] is True


@pytest.mark.asyncio
async def test_featured_group_event_hidden_from_non_member():
    today = date.today()
    async with async_session() as db:
        group = await get_group_by_slug(db, CORE_GROUP_SLUG)
        assert group is not None
        member = await get_or_create_user(db, telegram_id=940_003, username="m", first_name="M")
        outsider = await get_or_create_user(db, telegram_id=940_004, username="o", first_name="O")
        await add_user_to_group(db, member, group, notify=False)

        closed = Event(
            name="Core featured",
            description="",
            date=today + timedelta(days=6),
            time=time(12, 0),
            location="Moscow",
            audience_group_id=group.group_id,
            is_featured=True,
        )
        db.add(closed)
        await db.commit()
        await db.refresh(closed)

        member_list = await get_upcoming_events(db, user=member)
        outsider_list = await get_upcoming_events(db, user=outsider)
        member_featured = [
            row.event for row in member_list if row.event.event_id == closed.event_id
        ]
        outsider_ids = {row.event.event_id for row in outsider_list}

        assert len(member_featured) == 1
        assert member_featured[0].is_featured is True
        assert closed.event_id not in outsider_ids
