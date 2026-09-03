from __future__ import annotations

from datetime import date, time

from app.models.event import Event
from app.models.user import User
from app.services.admin_notifications import (
    build_admin_application_message,
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


def test_format_user_mention_keeps_underscore_in_username():
    assert format_user_mention(_user(username="nik_trishin")) == "@nik_trishin"


def test_format_user_mention_without_username():
    assert format_user_mention(_user(username=None, first_name="Иван")) == "Иван"


def test_format_user_mention_escapes_html_in_first_name():
    assert format_user_mention(_user(username=None, first_name="A<b>")) == "A&lt;b&gt;"


def test_escape_markdown_special_chars():
    assert escape_markdown("meet_up *beta*") == "meet\\_up \\*beta\\*"


def test_build_admin_registration_message_register():
    message = build_admin_registration_message(_user(), _event(), 5, registered=True)
    assert message == (
        "@anna будет на <b>Встреча</b> <b>Вс, 28 июня, 19:00</b>\n"
        "Всего гостей: 5"
    )


def test_build_admin_registration_message_cancel():
    message = build_admin_registration_message(_user(), _event(), 4, registered=False)
    assert message == (
        "@anna отменил(а) регистрацию на <b>Встреча</b> <b>Вс, 28 июня, 19:00</b>\n"
        "Всего гостей: 4"
    )


def test_build_admin_registration_message_with_plus_one():
    message = build_admin_registration_message(
        _user(), _event(), 6, registered=True, party_size=2
    )
    assert message == (
        "@anna будет на (+1) <b>Встреча</b> <b>Вс, 28 июня, 19:00</b>\n"
        "Всего гостей: 6"
    )


def test_build_admin_registration_message_escapes_event_name():
    message = build_admin_registration_message(_user(), _event("Встреча <VIP>"), 2, registered=True)
    assert "<b>Встреча &lt;VIP&gt;</b>" in message


def test_build_admin_application_message():
    message = build_admin_application_message(_user(), _event(), 3, party_size=1)
    assert message == (
        "@anna подал(а) заявку на <b>Встреча</b> <b>Вс, 28 июня, 19:00</b>\n"
        "Гостей в заявке: 1\n"
        "Всего гостей: 3"
    )


def test_build_admin_registration_message_underscore_username_is_html():
    message = build_admin_registration_message(
        _user(username="nik_trishin"), _event(), 1, registered=True
    )
    assert message.startswith("@nik_trishin будет на <b>")
    assert "*" not in message
