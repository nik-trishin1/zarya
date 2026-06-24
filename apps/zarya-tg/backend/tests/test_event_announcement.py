from __future__ import annotations

from datetime import date, time

from app.models.event import Event
from app.services.event_announcement import build_event_startapp_link, build_new_event_announcement


def _event() -> Event:
    return Event(
        event_id=42,
        name="Встреча у озера",
        description="Возьмите плед.",
        date=date(2026, 6, 28),
        time=time(19, 0),
        location="Москва",
        cover_image_url=None,
    )


def test_build_event_startapp_link():
    assert build_event_startapp_link("zarya_friends_bot", 42) == (
        "https://t.me/zarya_friends_bot?startapp=event_42"
    )


def test_build_new_event_announcement_puts_name_before_link():
    message = build_new_event_announcement(_event(), "zarya_friends_bot")
    assert message.startswith("🌅 Новое событие!")
    assert "📌 Встреча у озера ·" in message
    assert "📍 Москва" in message
    assert "Возьмите плед." in message
    link = "https://t.me/zarya_friends_bot?startapp=event_42"
    assert message.endswith(f"Встреча у озера\n{link}")


def test_build_new_event_announcement_omits_empty_description():
    event = _event()
    event.description = "   "
    message = build_new_event_announcement(event, "zarya_friends_bot")
    assert "Возьмите плед." not in message
    assert "startapp=event_42" in message
