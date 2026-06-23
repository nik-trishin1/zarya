from __future__ import annotations

import pytest
from sqlalchemy import select

from app.database import async_session, engine, Base
from app.models.media_file import MediaFile
from app.services.storage import normalize_cover_image_url, save_cover_image_bytes


@pytest.fixture(autouse=True)
async def ensure_tables():
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def test_normalize_cover_image_url_absolute_backend():
    url = "https://zarya-production-be.up.railway.app/uploads/abc123.jpg"
    assert normalize_cover_image_url(url) == "/uploads/abc123.jpg"


def test_normalize_cover_image_url_media():
    assert normalize_cover_image_url("/media/abc123def456") == "/media/abc123def456"
    url = "https://zarya-production-fe.up.railway.app/media/abc123def456"
    assert normalize_cover_image_url(url) == "/media/abc123def456"


def test_normalize_cover_image_url_relative():
    assert normalize_cover_image_url("/uploads/abc123.jpg") == "/uploads/abc123.jpg"


def test_normalize_cover_image_url_none():
    assert normalize_cover_image_url(None) is None


@pytest.mark.asyncio
async def test_save_cover_image_bytes_persists_in_database():
    # Minimal valid JPEG header bytes for extension validation
    content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    url = await save_cover_image_bytes(content, "cover.jpg")
    assert url.startswith("/media/")
    media_id = url.removeprefix("/media/")

    async with async_session() as db:
        result = await db.execute(select(MediaFile).where(MediaFile.media_id == media_id))
        media = result.scalar_one_or_none()

    assert media is not None
    assert media.content_type == "image/jpeg"
    assert media.data == content


@pytest.mark.asyncio
async def test_serve_media_endpoint(client):
    content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    url = await save_cover_image_bytes(content, "cover.jpg")
    media_id = url.removeprefix("/media/")

    response = await client.get(f"/media/{media_id}")
    assert response.status_code == 200
    assert response.content == content
    assert response.headers["content-type"].startswith("image/jpeg")
