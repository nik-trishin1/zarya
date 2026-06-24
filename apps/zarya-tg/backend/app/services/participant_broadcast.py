from __future__ import annotations

from aiogram import Bot

from app.config import get_settings
from app.models.event import Event
from app.models.user import User
from app.services.telegram_delivery import deliver_bot_messages_to_users
from app.utils.formatting import format_event_date

MAX_BROADCAST_BODY_LENGTH = 3500
TELEGRAM_MESSAGE_LIMIT = 4096


def build_participant_broadcast_message(event: Event, body: str) -> str:
    header = f"📌 {event.name} · {format_event_date(event.date, event.time)}"
    return f"{header}\n\n{body.strip()}"


def build_broadcast_preview(event: Event, body: str, recipient_count: int) -> str:
    message = build_participant_broadcast_message(event, body)
    return (
        f"Проверьте сообщение. Получателей: {recipient_count}\n\n"
        f"———\n{message}\n———"
    )


def validate_broadcast_body(body: str) -> str | None:
    trimmed = body.strip()
    if not trimmed:
        return "Сообщение не может быть пустым."
    if len(trimmed) > MAX_BROADCAST_BODY_LENGTH:
        return f"Сообщение слишком длинное. Максимум — {MAX_BROADCAST_BODY_LENGTH} символов."
    return None


async def send_participant_broadcast(
    users: list[User],
    event: Event,
    body: str,
) -> tuple[int, int, int]:
    """Returns (sent_count, blocked_count, other_failed_count)."""
    settings = get_settings()
    if not settings.bot_token_configured or not users:
        return 0, 0, 0

    bot = Bot(token=settings.bot_token.strip())
    message = build_participant_broadcast_message(event, body)
    if len(message) > TELEGRAM_MESSAGE_LIMIT:
        message = message[: TELEGRAM_MESSAGE_LIMIT - 1] + "…"

    context = f"participant_broadcast event_id={event.event_id}"
    try:
        return await deliver_bot_messages_to_users(bot, users, message, context=context)
    finally:
        await bot.session.close()
