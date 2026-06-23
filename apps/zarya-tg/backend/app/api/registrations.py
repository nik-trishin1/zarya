from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.schemas.event import EventResponse
from app.schemas.registration import RegistrationResponse
from app.services.events import (
    cancel_registration,
    get_event_detail,
    get_upcoming_events,
    register_user,
)
from app.services.admin_notifications import notify_admins_registration_change
from app.utils.calendar import (
    build_google_calendar_url,
    build_outlook_calendar_url,
    build_yahoo_calendar_url,
    generate_ics,
)
from app.utils.calendar_tokens import create_calendar_token, verify_calendar_token
from app.utils.formatting import event_to_response, format_event_date

router = APIRouter(tags=["registrations"])


async def _require_registered_event(
    db: AsyncSession, event_id: int, user: User
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
    return event


async def get_calendar_user(
    event_id: int,
    calendar_token: str | None = Query(None, alias="calendar_token"),
    x_telegram_init_data: str | None = Header(None, alias="X-Telegram-Init-Data"),
    init_data: str | None = Query(None, alias="initData"),
    db: AsyncSession = Depends(get_db),
) -> User:
    if calendar_token:
        settings = get_settings()
        user_id = verify_calendar_token(calendar_token, event_id, settings.secret_key)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ссылка для календаря устарела, откройте событие и попробуйте снова",
            )
        result = await db.execute(select(User).where(User.user_id == user_id))
        token_user = result.scalar_one_or_none()
        if token_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
        return token_user

    return await get_current_user(x_telegram_init_data, init_data, db)


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
    await notify_admins_registration_change(user, event, reg_count, registered=True)
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

    await notify_admins_registration_change(user, event, reg_count, registered=False)
    return RegistrationResponse(
        message=f"Вы отменили регистрацию на {event.name}",
        registration_count=reg_count,
        is_registered=is_registered,
    )


@router.get("/registrations/{event_id}/calendar-links")
async def get_calendar_links(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    event = await _require_registered_event(db, event_id, user)
    settings = get_settings()
    token = create_calendar_token(user.user_id, event_id, settings.secret_key)
    return {
        "google_url": build_google_calendar_url(event),
        "outlook_url": build_outlook_calendar_url(event),
        "yahoo_url": build_yahoo_calendar_url(event),
        "ics_token": token,
    }


@router.get("/registrations/{event_id}/calendar-token")
async def get_calendar_download_token(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Deprecated: use /calendar-links."""
    event = await _require_registered_event(db, event_id, user)
    settings = get_settings()
    token = create_calendar_token(user.user_id, event_id, settings.secret_key)
    return {"token": token, "google_url": build_google_calendar_url(event)}


@router.get("/events/{event_id}/calendar")
async def download_calendar(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_calendar_user),
):
    event = await _require_registered_event(db, event_id, user)

    ics_content = generate_ics(event)
    filename = f"zarya-{event.event_id}.ics"
    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
