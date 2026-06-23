from __future__ import annotations

import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.config import get_settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
DEFAULT_COVER_URL = "/static/default-cover.svg"


def ensure_upload_dir() -> Path:
    settings = get_settings()
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


async def save_cover_image(file: UploadFile) -> str:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Only JPEG and PNG images are allowed")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("Image must be smaller than 5MB")

    upload_path = ensure_upload_dir()
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_path / filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    settings = get_settings()
    return f"{settings.api_base_url.rstrip('/')}/uploads/{filename}"


async def save_cover_image_bytes(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Only JPEG and PNG images are allowed")
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("Image must be smaller than 5MB")

    upload_path = ensure_upload_dir()
    new_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_path / new_filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    settings = get_settings()
    return f"{settings.api_base_url.rstrip('/')}/uploads/{new_filename}"
