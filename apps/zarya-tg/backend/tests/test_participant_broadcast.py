from __future__ import annotations

from datetime import date, time

from app.models.event import Event
from app.services.participant_broadcast import (
    build_broadcast_preview,
    build_participant_broadcast_message,
    validate_broadcast_body,
)


def _event() -> Event:
    return Event(
        event_id=1,
        name="Встреча у озера",
        description="",
        date=date(2026, 6, 28),
        time=time(19, 0),
        location="Москва",
        cover_image_url=None,
    )


def test_build_participant_broadcast_message():
    message = build_participant_broadcast_message(_event(), "Возьмите с собой плед.")
    assert message.startswith("📌 Встреча у озера ·")
    assert message.endswith("Возьмите с собой плед.")


def test_build_broadcast_preview_includes_recipient_count():
    preview = build_broadcast_preview(_event(), "Тест", 3)
    assert "Получателей: 3" in preview
    assert "Тест" in preview


def test_validate_broadcast_body_rejects_empty():
    assert validate_broadcast_body("   ") == "Сообщение не может быть пустым."


def test_validate_broadcast_body_accepts_text():
    assert validate_broadcast_body("Привет!") is None
