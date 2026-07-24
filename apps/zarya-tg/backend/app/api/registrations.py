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
from app.schemas.registration import (
    RegistrationCreate,
    RegistrationPartyUpdate,
    RegistrationResponse,
)
from app.services.events import (
    cancel_registration,
    get_event_detail,
    get_upcoming_events,
    register_user,
    update_party_size,
)
from app.services.admin_notifications import notify_admins_registration_change
from app.utils.calendar import (
    build_google_calendar_url,
    build_outlook_calendar_url,
    build_yahoo_calendar_url,
    generate_ics,
)
from app.utils.calendar_tokens import create_calendar_token, verify_calendar_token
from app.utils.formatting import attendance_to_response, format_event_date

router = APIRouter(tags=["registrations"])


async def _require_registered_event(
    db: AsyncSession, event_id: int, user: User
):
    detail = await get_event_detail(db, event_id, user)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    if not detail.is_registered:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Календарь доступен только зарегистрированным участникам",
        )
    return detail.event


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


def _registration_error(exc: ValueError) -> HTTPException:
    code = str(exc)
    if code == "Event not found":
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    if code == "Already registered":
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Вы уже зарегистрированы")
    if code == "Event past":
        return HTTPException(status_code=status.HTTP_410_GONE, detail="Событие уже прошло")
    if code == "Event full":
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Мест нет")
    if code == "Not registered":
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Регистрация не найдена")
    if code == "Invalid party size":
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Некорректное число мест")
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/registrations/my", response_model=list[EventResponse])
async def my_registrations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = await get_upcoming_events(db, user=user, registered_only=True)
    return [attendance_to_response(row) for row in rows]


@router.post("/registrations/{event_id}", response_model=RegistrationResponse)
async def register_for_event(
    event_id: int,
    body: RegistrationCreate | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    party_size = body.party_size if body is not None else 1
    try:
        attendance = await register_user(db, user, event_id, party_size=party_size)
    except ValueError as e:
        raise _registration_error(e) from e

    date_str = format_event_date(attendance.event.date, attendance.event.time)
    if attendance.party_size > 1:
        message = (
            f"Вы зарегистрированы на {attendance.event.name} на {date_str} "
            f"(+{attendance.party_size - 1})"
        )
    else:
        message = f"Вы зарегистрированы на {attendance.event.name} на {date_str}"
    await notify_admins_registration_change(
        user,
        attendance.event,
        attendance.registration_count,
        registered=True,
        party_size=attendance.party_size,
    )
    return RegistrationResponse(
        message=message,
        registration_count=attendance.registration_count,
        is_registered=attendance.is_registered,
        party_size=attendance.party_size,
    )


@router.patch("/registrations/{event_id}", response_model=RegistrationResponse)
async def update_registration_party_size(
    event_id: int,
    body: RegistrationPartyUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        attendance = await update_party_size(db, user, event_id, body.party_size)
    except ValueError as e:
        raise _registration_error(e) from e

    if attendance.party_size > 1:
        message = f"Добавлен +{attendance.party_size - 1} к регистрации на {attendance.event.name}"
    else:
        message = f"+1 убран с регистрации на {attendance.event.name}"

    await notify_admins_registration_change(
        user,
        attendance.event,
        attendance.registration_count,
        registered=True,
        party_size=attendance.party_size,
    )
    return RegistrationResponse(
        message=message,
        registration_count=attendance.registration_count,
        is_registered=attendance.is_registered,
        party_size=attendance.party_size,
    )


@router.delete("/registrations/{event_id}", response_model=RegistrationResponse)
async def cancel_event_registration(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        attendance = await cancel_registration(db, user, event_id)
    except ValueError as e:
        raise _registration_error(e) from e

    await notify_admins_registration_change(
        user,
        attendance.event,
        attendance.registration_count,
        registered=False,
        party_size=0,
    )
    return RegistrationResponse(
        message=f"Вы отменили регистрацию на {attendance.event.name}",
        registration_count=attendance.registration_count,
        is_registered=attendance.is_registered,
        party_size=0,
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
