from __future__ import annotations

import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.config import get_settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
DEFAULT_COVER_URL = "/static/default-cover.svg"

_IMAGE_TOO_LARGE = f"Изображение слишком большое. Максимальный размер — {MAX_FILE_SIZE_MB} МБ."
_INVALID_FORMAT = "Допустимы только изображения JPEG и PNG."


def image_too_large_message() -> str:
    return _IMAGE_TOO_LARGE


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

    settings = get_settings()
    return f"{settings.api_base_url.rstrip('/')}/uploads/{filename}"


async def save_cover_image_bytes(content: bytes, filename: str) -> str:
    validate_cover_image_bytes(content, filename)

    ext = Path(filename).suffix.lower()
    upload_path = ensure_upload_dir()
    new_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_path / new_filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    settings = get_settings()
    return f"{settings.api_base_url.rstrip('/')}/uploads/{new_filename}"
