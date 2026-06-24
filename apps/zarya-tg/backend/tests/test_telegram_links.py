from __future__ import annotations

import pytest

from app.utils.telegram_links import build_event_share_text, build_event_startapp_link


def test_build_event_startapp_link_includes_both_start_params():
    link = build_event_startapp_link("zarya_friends_bot", 42)
    assert "startapp=event_42" in link
    assert "startApp=event_42" in link


@pytest.mark.parametrize(
    ("description", "expected_tail"),
    [
        ("Описание", "\n\nОписание"),
        ("", ""),
    ],
)
def test_build_event_share_text(description: str, expected_tail: str):
    link = "https://t.me/bot?startapp=event_1&startApp=event_1"
    text = build_event_share_text("Событие", link, description)
    assert text == f"Событие\n{link}{expected_tail}"
