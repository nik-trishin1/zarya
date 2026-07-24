from __future__ import annotations

from datetime import date, time

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import async_session, engine, Base
from app.main import app
from app.models.event import Event


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
async def test_get_event_returns_max_participants(client: AsyncClient):
    async with async_session() as db:
        event = Event(
            name="Limited",
            description="",
            date=date(2026, 12, 1),
            time=time(19, 0),
            location="Moscow",
            max_participants=20,
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        event_id = event.event_id

    response = await client.get(f"/api/events/{event_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["max_participants"] == 20
    assert payload["is_full"] is False
    assert payload["allows_plus_one"] is True
    assert payload["allows_sharing"] is True
    assert payload["audience_group_id"] is None
