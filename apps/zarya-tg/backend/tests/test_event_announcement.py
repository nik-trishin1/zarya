from __future__ import annotations

from datetime import date, time

from app.models.event import Event
from app.services.event_announcement import build_new_event_announcement
from app.utils.telegram_links import build_event_startapp_link


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


def test_build_event_startapp_link_uses_startapp_only():
    link = build_event_startapp_link("zarya_friends_bot", 42)
    assert link == "https://t.me/zarya_friends_bot?startapp=event_42"
    assert "startApp" not in link
    assert "mode=" not in link


def test_build_event_startapp_link_with_short_name():
    link = build_event_startapp_link("zarya_friends_bot", 42, app_short_name="zarya")
    assert link.startswith("https://t.me/zarya_friends_bot/zarya?")
    assert "startapp=event_42" in link


def test_build_new_event_announcement_puts_name_before_link():
    message = build_new_event_announcement(_event(), "zarya_friends_bot")
    assert message.startswith("🌅 Новое событие!")
    assert "📌 Встреча у озера ·" in message
    assert "📍 Москва" in message
    assert "Возьмите плед." in message
    link = build_event_startapp_link("zarya_friends_bot", 42)
    assert message.endswith(f"Встреча у озера\n{link}")


def test_build_new_event_announcement_omits_empty_description():
    event = _event()
    event.description = "   "
    message = build_new_event_announcement(event, "zarya_friends_bot")
    assert "Возьмите плед." not in message
    assert "startapp=event_42" in message
