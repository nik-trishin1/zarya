from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlencode
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event as ICalEvent

from app.models.event import Event

MOSCOW_TZ = ZoneInfo("Europe/Moscow")
EVENT_DURATION = timedelta(hours=2)
GOOGLE_CALENDAR_BASE = "https://calendar.google.com/calendar/render"
OUTLOOK_CALENDAR_BASE = "https://outlook.live.com/calendar/0/deeplink/compose"
YAHOO_CALENDAR_BASE = "https://calendar.yahoo.com/"


def event_start_datetime(event: Event) -> datetime:
    return datetime.combine(event.date, event.time, tzinfo=MOSCOW_TZ)


def event_end_datetime(event: Event) -> datetime:
    return event_start_datetime(event) + EVENT_DURATION


def _calendar_details(event: Event) -> str:
    return f"{event.description}\n\nЛокация: {event.location}"


def build_google_calendar_url(event: Event) -> str:
    start_dt = event_start_datetime(event)
    end_dt = event_end_datetime(event)
    params = {
        "action": "TEMPLATE",
        "text": event.name,
        "dates": f"{start_dt.strftime('%Y%m%dT%H%M%S')}/{end_dt.strftime('%Y%m%dT%H%M%S')}",
        "ctz": "Europe/Moscow",
        "details": _calendar_details(event),
        "location": event.location,
    }
    return f"{GOOGLE_CALENDAR_BASE}?{urlencode(params, quote_via=quote)}"


def build_outlook_calendar_url(event: Event) -> str:
    start_dt = event_start_datetime(event)
    end_dt = event_end_datetime(event)
    params = {
        "path": "/calendar/action/compose",
        "rru": "addevent",
        "subject": event.name,
        "startdt": start_dt.isoformat(),
        "enddt": end_dt.isoformat(),
        "body": _calendar_details(event),
        "location": event.location,
    }
    return f"{OUTLOOK_CALENDAR_BASE}?{urlencode(params, quote_via=quote)}"


def build_yahoo_calendar_url(event: Event) -> str:
    start_dt = event_start_datetime(event)
    duration_minutes = int(EVENT_DURATION.total_seconds() // 60)
    params = {
        "v": 60,
        "title": event.name,
        "st": start_dt.strftime('%Y%m%dT%H%M%S'),
        "dur": f"{duration_minutes // 60:02d}{duration_minutes % 60:02d}",
        "desc": _calendar_details(event),
        "in_loc": event.location,
    }
    return f"{YAHOO_CALENDAR_BASE}?{urlencode(params, quote_via=quote)}"


def generate_ics(event: Event) -> bytes:
    cal = Calendar()
    cal.add("prodid", "-//zarya//zarya-tg//RU")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")

    start_dt = event_start_datetime(event)
    end_dt = event_end_datetime(event)
    now_utc = datetime.now(timezone.utc)

    ical_event = ICalEvent()
    ical_event.add("uid", f"zarya-event-{event.event_id}@zarya.app")
    ical_event.add("dtstamp", now_utc)
    ical_event.add("created", now_utc)
    ical_event.add("last-modified", now_utc)
    ical_event.add("sequence", 0)
    ical_event.add("status", "CONFIRMED")
    ical_event.add("transp", "OPAQUE")
    ical_event.add("summary", event.name)
    ical_event.add("location", event.location)
    ical_event.add("description", event.description)
    ical_event.add("dtstart", start_dt.astimezone(timezone.utc))
    ical_event.add("dtend", end_dt.astimezone(timezone.utc))

    cal.add_component(ical_event)
    return cal.to_ical()
