from __future__ import annotations

from datetime import date, time, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import async_session, engine, Base
from app.main import app
from app.models.event import Event
from app.utils.pricing import NARROW_NBSP, PricePairError
from app.services.events import create_event, update_event
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


async def _admin():
    async with async_session() as db:
        return await get_or_create_user(db, telegram_id=950_001, username="price_admin", first_name="A")


@pytest.mark.asyncio
async def test_create_event_stores_price_pair():
    admin = await _admin()
    async with async_session() as db:
        event = await create_event(
            db,
            name="Paid hangout",
            description="",
            event_date=date.today() + timedelta(days=3),
            event_time=time(19, 0),
            location="Moscow",
            cover_image_url=None,
            admin_user=admin,
            price_amount_minor=100_000,
            price_currency="RUB",
        )
        assert event.price_amount_minor == 100_000
        assert event.price_currency == "RUB"


@pytest.mark.asyncio
async def test_create_event_defaults_price_unset():
    admin = await _admin()
    async with async_session() as db:
        event = await create_event(
            db,
            name="Free hangout",
            description="",
            event_date=date.today() + timedelta(days=3),
            event_time=time(19, 0),
            location="Moscow",
            cover_image_url=None,
            admin_user=admin,
        )
        assert event.price_amount_minor is None
        assert event.price_currency is None


@pytest.mark.asyncio
async def test_create_event_rejects_currency_without_amount():
    admin = await _admin()
    async with async_session() as db:
        with pytest.raises(PricePairError):
            await create_event(
                db,
                name="Broken",
                description="",
                event_date=date.today() + timedelta(days=3),
                event_time=time(19, 0),
                location="Moscow",
                cover_image_url=None,
                admin_user=admin,
                price_currency="RUB",
            )


@pytest.mark.asyncio
async def test_update_event_can_change_and_clear_price():
    admin = await _admin()
    async with async_session() as db:
        event = await create_event(
            db,
            name="Editable",
            description="",
            event_date=date.today() + timedelta(days=4),
            event_time=time(20, 0),
            location="Moscow",
            cover_image_url=None,
            admin_user=admin,
            price_amount_minor=100_000,
            price_currency="RUB",
        )
        updated = await update_event(
            db, event, price_amount_minor=250_000, price_currency="RUB"
        )
        assert updated.price_amount_minor == 250_000
        cleared = await update_event(
            db, event, price_amount_minor=None, price_currency=None
        )
        assert cleared.price_amount_minor is None
        assert cleared.price_currency is None


@pytest.mark.asyncio
async def test_api_returns_price_label(client: AsyncClient):
    async with async_session() as db:
        event = Event(
            name="Priced",
            description="",
            date=date.today() + timedelta(days=5),
            time=time(18, 0),
            location="Moscow",
            price_amount_minor=100_000,
            price_currency="RUB",
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        event_id = event.event_id

    response = await client.get(f"/api/events/{event_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["price_amount_minor"] == 100_000
    assert payload["price_currency"] == "RUB"
    assert payload["price_label"] == f"1{NARROW_NBSP}000 ₽"


@pytest.mark.asyncio
async def test_api_price_null_when_unset(client: AsyncClient):
    async with async_session() as db:
        event = Event(
            name="Unpriced",
            description="",
            date=date.today() + timedelta(days=5),
            time=time(18, 0),
            location="Moscow",
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        event_id = event.event_id

    response = await client.get(f"/api/events/{event_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["price_amount_minor"] is None
    assert payload["price_currency"] is None
    assert payload["price_label"] is None
    assert "Бесплатно" not in str(payload)
