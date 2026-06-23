from __future__ import annotations

import uuid
from pathlib import Path
from urllib.parse import urlparse

import aiofiles
from fastapi import UploadFile

from app.config import get_settings

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


def image_too_large_message() -> str:
    return _IMAGE_TOO_LARGE


def normalize_cover_image_url(url: str | None) -> str | None:
    """Return a same-origin path (/uploads/... or /static/...) for API responses."""
    if not url:
        return None
    trimmed = url.strip()
    if trimmed.startswith("/uploads/") or trimmed.startswith("/static/"):
        return trimmed
    path = urlparse(trimmed).path
    if path.startswith("/uploads/") or path.startswith("/static/"):
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


async def save_cover_image(file: UploadFile) -> str:
    content = await file.read()
    validate_cover_image_bytes(content, file.filename or "cover.jpg")

    ext = Path(file.filename or "").suffix.lower()
    upload_path = ensure_upload_dir()
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_path / filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return f"/uploads/{filename}"


async def save_cover_image_bytes(content: bytes, filename: str) -> str:
    validate_cover_image_bytes(content, filename)

    ext = Path(filename).suffix.lower()
    upload_path = ensure_upload_dir()
    new_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_path / new_filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return f"/uploads/{new_filename}"
