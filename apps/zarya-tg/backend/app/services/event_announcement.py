from __future__ import annotations

from aiogram import Bot

from app.config import get_settings
from app.models.event import Event
from app.models.user import User
from app.services.telegram_delivery import deliver_bot_messages_to_users
from app.utils.formatting import format_event_date

MAX_DESCRIPTION_LENGTH = 500
TELEGRAM_MESSAGE_LIMIT = 4096


def build_event_startapp_link(bot_username: str, event_id: int) -> str:
    username = bot_username.lstrip("@")
    return f"https://t.me/{username}?startapp=event_{event_id}"


def build_new_event_announcement(event: Event, bot_username: str) -> str:
    header = f"🌅 Новое событие!\n\n📌 {event.name} · {format_event_date(event.date, event.time)}"
    location_line = f"📍 {event.location}"
    parts = [header, location_line]

    description = (event.description or "").strip()
    if description:
        if len(description) > MAX_DESCRIPTION_LENGTH:
            description = description[: MAX_DESCRIPTION_LENGTH - 1] + "…"
        parts.append(description)

    link = build_event_startapp_link(bot_username, event.event_id)
    parts.append(f"{event.name}\n{link}")

    message = "\n\n".join(parts)
    if len(message) > TELEGRAM_MESSAGE_LIMIT:
        message = message[: TELEGRAM_MESSAGE_LIMIT - 1] + "…"
    return message


async def send_new_event_announcement(
    users: list[User],
    event: Event,
    bot_username: str,
) -> tuple[int, int, int]:
    """Returns (sent_count, blocked_count, other_failed_count)."""
    settings = get_settings()
    if not settings.bot_token_configured or not users:
        return 0, 0, 0

    message = build_new_event_announcement(event, bot_username)
    bot = Bot(token=settings.bot_token.strip())
    context = f"new_event_announcement event_id={event.event_id}"
    try:
        return await deliver_bot_messages_to_users(
            bot,
            users,
            message,
            context=context,
        )
    finally:
        await bot.session.close()
