from __future__ import annotations

from datetime import date, time

from app.schemas.event import EventDetailResponse, EventResponse
from app.services.events import MOSCOW_TZ


RU_MONTHS = [
    "",
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
]

RU_WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def format_event_date(event_date: date, event_time: time) -> str:
    weekday = RU_WEEKDAYS[event_date.weekday()]
    month = RU_MONTHS[event_date.month]
    return f"{weekday}, {event_date.day} {month}, {event_time.strftime('%H:%M')}"


def event_to_response(event, reg_count: int, is_registered: bool) -> EventResponse:
    return EventResponse(
        event_id=event.event_id,
        name=event.name,
        description=event.description,
        date=event.date,
        time=event.time,
        location=event.location,
        cover_image_url=event.cover_image_url,
        registration_count=reg_count,
        is_registered=is_registered,
    )


def event_to_detail(event, reg_count: int, is_registered: bool) -> EventDetailResponse:
    return EventDetailResponse(
        event_id=event.event_id,
        name=event.name,
        description=event.description,
        date=event.date,
        time=event.time,
        location=event.location,
        cover_image_url=event.cover_image_url,
        registration_count=reg_count,
        is_registered=is_registered,
    )
