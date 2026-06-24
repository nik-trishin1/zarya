from __future__ import annotations

import pytest
from sqlalchemy import select

from app.database import async_session, engine, Base
from app.models.user import User
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
async def test_get_or_create_user_inserts_on_first_contact():
    async with async_session() as db:
        user = await get_or_create_user(db, telegram_id=424242, username="newbie", first_name="New")

    assert user.user_id is not None
    assert user.telegram_id == 424242
    assert user.username == "newbie"


@pytest.mark.asyncio
async def test_get_or_create_user_updates_profile():
    async with async_session() as db:
        await get_or_create_user(db, telegram_id=525252, username="old", first_name="Old")
        user = await get_or_create_user(db, telegram_id=525252, username="fresh", first_name="Fresh")

    assert user.username == "fresh"
    assert user.first_name == "Fresh"

    async with async_session() as db:
        result = await db.execute(select(User).where(User.telegram_id == 525252))
        stored = result.scalar_one()
    assert stored.username == "fresh"
