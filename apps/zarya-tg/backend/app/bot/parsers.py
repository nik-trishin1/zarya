from __future__ import annotations

from datetime import date, datetime, time

from dateutil import parser as date_parser


def parse_date(text: str) -> date | None:
    text = text.strip()
    for fmt in ("%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return date_parser.parse(text, dayfirst=True).date()
    except (ValueError, TypeError):
        return None


def parse_time(text: str) -> time | None:
    text = text.strip()
    for fmt in ("%H:%M", "%H.%M"):
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    return None


def format_date_ru(d: date) -> str:
    months = [
        "", "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря",
    ]
    return f"{d.day} {months[d.month]} {d.year}"


def format_time_ru(t: time) -> str:
    return t.strftime("%H:%M")
