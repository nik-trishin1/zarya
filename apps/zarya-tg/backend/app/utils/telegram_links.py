from __future__ import annotations

from urllib.parse import urlencode


def build_event_start_param(event_id: int) -> str:
    return f"event_{event_id}"


def build_event_startapp_link(
    bot_username: str,
    event_id: int,
    *,
    app_short_name: str | None = None,
) -> str:
    """Build a Mini App direct link compatible with iOS and Android."""
    username = bot_username.lstrip("@")
    start_param = build_event_start_param(event_id)
    query = urlencode({"startapp": start_param})
    short_name = (app_short_name or "").strip().lstrip("@")
    if short_name:
        return f"https://t.me/{username}/{short_name}?{query}"
    return f"https://t.me/{username}?{query}"
