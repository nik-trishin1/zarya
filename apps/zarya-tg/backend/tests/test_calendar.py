from datetime import date, time

from app.models.event import Event
from app.utils.calendar import build_google_calendar_url, generate_ics


def _sample_event() -> Event:
    return Event(
        event_id=1,
        name="Встреча друзей",
        description="Ужин и разговоры",
        date=date(2025, 7, 15),
        time=time(19, 0),
        location="Москва, парк",
        cover_image_url=None,
        created_by_admin_id=1,
    )


def test_generate_ics_has_dtstamp_and_utc():
    ics = generate_ics(_sample_event()).decode()
    assert "DTSTAMP" in ics
    assert "DTSTART" in ics and "Z" in ics
    assert "DTEND" in ics and "Z" in ics
    assert "BEGIN:VEVENT" in ics


def test_build_google_calendar_url_contains_required_params():
    url = build_google_calendar_url(_sample_event())
    assert "calendar.google.com/calendar/render" in url
    assert "action=TEMPLATE" in url
    assert "text=" in url
    assert "dates=" in url
    assert "ctz=Europe%2FMoscow" in url
    assert "20250715T190000" in url
    assert "20250715T210000" in url
