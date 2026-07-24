from __future__ import annotations

from app.bot.participants import (
    expand_participant_lines,
    format_participant_line,
    format_participants_message,
)
from app.models.user import User


def _user(first_name: str = "Иван", username: str | None = "ivan") -> User:
    return User(user_id=1, telegram_id=100, username=username, first_name=first_name)


def test_format_participant_line_with_username():
    assert format_participant_line(1, _user()) == "1. Иван @ivan"


def test_format_participant_line_without_username():
    assert format_participant_line(2, _user(username=None, first_name="Мария")) == "2. Мария"


def test_format_participant_line_plus_one():
    assert format_participant_line(2, _user(first_name="Никита"), plus_one_index=1) == "2. Никита + 1"


def test_expand_participant_lines_duplicates_plus_one():
    nikita = _user(first_name="Никита", username="nikita")
    other = _user(first_name="Другой гость", username="other")
    lines = expand_participant_lines([(nikita, 2), (other, 1)])
    assert lines == [
        "1. Никита @nikita",
        "2. Никита + 1",
        "3. Другой гость @other",
    ]


def test_format_participants_message_empty():
    assert format_participants_message("Встреча", []) == (
        "Участники: Встреча\n\nПока никто не зарегистрирован."
    )


def test_format_participants_message_numbered_list():
    users = [
        _user(first_name="Иван", username="ivan"),
        _user(first_name="Мария", username="masha"),
    ]
    message = format_participants_message("Встреча", users)
    assert "1. Иван @ivan" in message
    assert "2. Мария @masha" in message
    assert message.endswith("Всего: 2")


def test_format_participants_message_with_party_size():
    parties = [
        (_user(first_name="Никита", username="nikita"), 2),
        (_user(first_name="Другой гость", username="other"), 1),
    ]
    message = format_participants_message("Встреча", parties)
    assert "1. Никита @nikita" in message
    assert "2. Никита + 1" in message
    assert "3. Другой гость @other" in message
    assert message.endswith("Всего: 3")
