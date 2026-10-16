from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

# Configure before app modules cache settings / engine.
os.environ["ADMIN_TOKEN"] = "test-token"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test-link-qr.db"
os.environ["PUBLIC_BASE_URL"] = "http://test"

from app.config import get_settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

get_settings.cache_clear()


@pytest.fixture(autouse=True)
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"X-Admin-Token": "test-token"}
