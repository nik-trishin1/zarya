from __future__ import annotations

from urllib.parse import urlencode


def build_event_start_param(event_id: int) -> str:
    return f"event_{event_id}"


def build_event_share_text(name: str, link: str, description: str = "") -> str:
    """Share body: title, link, blank line, optional description."""
    lines = [name.strip(), link.strip()]
    desc = description.strip()
    if desc:
        lines.extend(["", desc])
    return "\n".join(lines)


def build_event_startapp_link(
    bot_username: str,
    event_id: int,
    *,
    app_short_name: str | None = None,
) -> str:
    """Build a Mini App direct link.

    Both startapp and startApp are required: lowercase routes to the Mini App,
    camelCase passes start_param on iOS. Prefer Direct Link path when short name
    is configured in BotFather.
    """
    username = bot_username.lstrip("@")
    start_param = build_event_start_param(event_id)
    query = urlencode([("startapp", start_param), ("startApp", start_param)])
    short_name = (app_short_name or "").strip().lstrip("@")
    if short_name:
        return f"https://t.me/{username}/{short_name}?{query}"
    return f"https://t.me/{username}?{query}"
