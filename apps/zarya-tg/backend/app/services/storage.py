from __future__ import annotations

import uuid
from pathlib import Path
from urllib.parse import urlparse

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import async_session
from app.models.media_file import MediaFile

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
DEFAULT_COVER_URL = "/static/default-cover.svg"

_IMAGE_TOO_LARGE = f"Изображение слишком большое. Максимальный размер — {MAX_FILE_SIZE_MB} МБ."
_INVALID_FORMAT = "Допустимы только изображения JPEG и PNG."

_MIME_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/pjpeg": ".jpg",
    "image/png": ".png",
}

_EXT_TO_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}

_MEDIA_PATH_PREFIXES = ("/uploads/", "/media/", "/static/")


def image_too_large_message() -> str:
    return _IMAGE_TOO_LARGE


def normalize_cover_image_url(url: str | None) -> str | None:
    """Return a same-origin path (/media/..., /uploads/..., /static/...) for API responses."""
    if not url:
        return None
    trimmed = url.strip()
    for prefix in _MEDIA_PATH_PREFIXES:
        if trimmed.startswith(prefix):
            return trimmed
    path = urlparse(trimmed).path
    for prefix in _MEDIA_PATH_PREFIXES:
        if path.startswith(prefix):
            return path
    return trimmed


def cover_filename_from_document(file_name: str | None, mime_type: str | None) -> str:
    name = (file_name or "").strip()
    if name:
        ext = Path(name).suffix.lower()
        if ext in ALLOWED_EXTENSIONS:
            return name
        stem = Path(name).stem or "cover"
    else:
        stem = "cover"
    ext = _MIME_TO_EXT.get((mime_type or "").lower(), ".jpg")
    return f"{stem}{ext}"


def content_type_for_filename(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return _EXT_TO_MIME.get(ext, "application/octet-stream")


def validate_cover_image_bytes(content: bytes, filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(_INVALID_FORMAT)
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(_IMAGE_TOO_LARGE)


def ensure_upload_dir() -> Path:
    settings = get_settings()
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


async def get_media_file(db: AsyncSession, media_id: str) -> MediaFile | None:
    result = await db.execute(select(MediaFile).where(MediaFile.media_id == media_id))
    return result.scalar_one_or_none()


async def save_media_bytes(content: bytes, filename: str) -> str:
    validate_cover_image_bytes(content, filename)
    media_id = uuid.uuid4().hex
    media = MediaFile(
        media_id=media_id,
        content_type=content_type_for_filename(filename),
        data=content,
    )
    async with async_session() as db:
        db.add(media)
        await db.commit()
    return f"/media/{media_id}"


async def save_cover_image(file: UploadFile) -> str:
    content = await file.read()
    return await save_cover_image_bytes(content, file.filename or "cover.jpg")


async def save_cover_image_bytes(content: bytes, filename: str) -> str:
    return await save_media_bytes(content, filename)


async def save_cover_image_to_disk(content: bytes, filename: str) -> str:
    """Legacy filesystem storage for local tooling; production uses database media."""
    validate_cover_image_bytes(content, filename)

    ext = Path(filename).suffix.lower()
    upload_path = ensure_upload_dir()
    new_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_path / new_filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return f"/uploads/{new_filename}"
