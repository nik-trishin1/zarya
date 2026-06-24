from __future__ import annotations

from datetime import date, time

from app.models.event import Event
from app.services.event_announcement import build_new_event_announcement
from app.utils.telegram_links import (
    build_event_share_text,
    build_event_startapp_link,
)


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


def test_build_event_startapp_link_includes_both_start_params():
    link = build_event_startapp_link("zarya_friends_bot", 42)
    assert link == "https://t.me/zarya_friends_bot?startapp=event_42&startApp=event_42"
    assert "mode=" not in link


def test_build_event_startapp_link_with_short_name():
    link = build_event_startapp_link("zarya_friends_bot", 42, app_short_name="zarya")
    assert link == "https://t.me/zarya_friends_bot/zarya?startapp=event_42&startApp=event_42"


def test_build_event_share_text_orders_title_link_description():
    text = build_event_share_text(
        "Встреча у озера",
        "https://t.me/zarya_friends_bot?startapp=event_42&startApp=event_42",
        "Возьмите плед.",
    )
    assert text == (
        "Встреча у озера\n"
        "https://t.me/zarya_friends_bot?startapp=event_42&startApp=event_42\n"
        "\n"
        "Возьмите плед."
    )


def test_build_new_event_announcement_ends_with_share_block():
    message = build_new_event_announcement(_event(), "zarya_friends_bot")
    assert message.startswith("🌅 Новое событие!")
    assert "📌 Встреча у озера ·" in message
    assert "📍 Москва" in message
    link = build_event_startapp_link("zarya_friends_bot", 42)
    assert message.endswith(build_event_share_text("Встреча у озера", link, "Возьмите плед."))
    assert message.count("Возьмите плед.") == 1


def test_build_new_event_announcement_omits_empty_description():
    event = _event()
    event.description = "   "
    message = build_new_event_announcement(event, "zarya_friends_bot")
    link = build_event_startapp_link("zarya_friends_bot", 42)
    assert message.endswith(build_event_share_text("Встреча у озера", link, ""))
    assert "startapp=event_42" in message
