from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.event import EventDetailResponse, EventResponse
from app.services.events import get_event_detail, get_upcoming_events
from app.utils.formatting import event_to_detail, event_to_response

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = await get_upcoming_events(db, user=user)
    return [event_to_response(event, reg_count, is_reg) for event, reg_count, is_reg in rows]


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    detail = await get_event_detail(db, event_id, user)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    event, reg_count, is_registered = detail
    return event_to_detail(event, reg_count, is_registered)
