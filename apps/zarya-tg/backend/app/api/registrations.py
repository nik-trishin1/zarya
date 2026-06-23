from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.event import EventResponse
from app.schemas.registration import RegistrationResponse
from app.services.events import (
    cancel_registration,
    generate_ics,
    get_event_by_id,
    get_event_detail,
    get_upcoming_events,
    register_user,
)
from app.utils.formatting import event_to_response, format_event_date

router = APIRouter(tags=["registrations"])


@router.get("/registrations/my", response_model=list[EventResponse])
async def my_registrations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = await get_upcoming_events(db, user=user, registered_only=True)
    return [event_to_response(event, reg_count, is_reg) for event, reg_count, is_reg in rows]


@router.post("/registrations/{event_id}", response_model=RegistrationResponse)
async def register_for_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        event, reg_count, is_registered = await register_user(db, user, event_id)
    except ValueError as e:
        if str(e) == "Event not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
        if str(e) == "Already registered":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Вы уже зарегистрированы")
        raise

    date_str = format_event_date(event.date, event.time)
    return RegistrationResponse(
        message=f"Вы зарегистрированы на {event.name} на {date_str}",
        registration_count=reg_count,
        is_registered=is_registered,
    )


@router.delete("/registrations/{event_id}", response_model=RegistrationResponse)
async def cancel_event_registration(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        event, reg_count, is_registered = await cancel_registration(db, user, event_id)
    except ValueError as e:
        if str(e) == "Not registered":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Регистрация не найдена")
        raise

    return RegistrationResponse(
        message=f"Вы отменили регистрацию на {event.name}",
        registration_count=reg_count,
        is_registered=is_registered,
    )


@router.get("/events/{event_id}/calendar")
async def download_calendar(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    detail = await get_event_detail(db, event_id, user)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")

    event, _, is_registered = detail
    if not is_registered:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Календарь доступен только зарегистрированным участникам",
        )

    ics_content = generate_ics(event)
    filename = f"zarya-{event.event_id}.ics"
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
