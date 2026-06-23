from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.storage import get_media_file

router = APIRouter(tags=["media"])

_MEDIA_ID_PATTERN = re.compile(r"^[a-f0-9]{32}$")


@router.get("/media/{media_id}")
async def serve_media(media_id: str, db: AsyncSession = Depends(get_db)) -> Response:
    if not _MEDIA_ID_PATTERN.match(media_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    media = await get_media_file(db, media_id)
    if media is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return Response(
        content=media.data,
        media_type=media.content_type,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
