from __future__ import annotations

from datetime import date, time

from app.models.event import Event
from app.models.user import User
from app.services.admin_notifications import (
    build_admin_registration_message,
    escape_markdown,
    format_user_mention,
)


def _event(name: str = "Встреча") -> Event:
    return Event(
        event_id=1,
        name=name,
        description="",
        date=date(2026, 6, 28),
        time=time(19, 0),
        location="Москва",
        cover_image_url=None,
    )


def _user(username: str | None = "anna", first_name: str | None = "Anna") -> User:
    return User(user_id=1, telegram_id=100, username=username, first_name=first_name)


def test_format_user_mention_with_username():
    assert format_user_mention(_user()) == "@anna"


def test_format_user_mention_without_username():
    assert format_user_mention(_user(username=None, first_name="Иван")) == "Иван"


def test_escape_markdown_special_chars():
    assert escape_markdown("meet_up *beta*") == "meet\\_up \\*beta\\*"


def test_build_admin_registration_message_register():
    message = build_admin_registration_message(_user(), _event(), 5, registered=True)
    assert message == (
        "@anna будет на *Встреча* *Вс, 28 июня, 19:00*\n"
        "Всего гостей: 5"
    )


def test_build_admin_registration_message_cancel():
    message = build_admin_registration_message(_user(), _event(), 4, registered=False)
    assert message == (
        "@anna отменил(а) регистрацию на *Встреча* *Вс, 28 июня, 19:00*\n"
        "Всего гостей: 4"
    )


def test_build_admin_registration_message_with_plus_one():
    message = build_admin_registration_message(
        _user(), _event(), 6, registered=True, party_size=2
    )
    assert message == (
        "@anna будет на (+1) *Встреча* *Вс, 28 июня, 19:00*\n"
        "Всего гостей: 6"
    )


def test_build_admin_registration_message_escapes_event_name():
    message = build_admin_registration_message(_user(), _event("Встреча *VIP*"), 2, registered=True)
    assert "*Встреча \\*VIP\\**" in message
