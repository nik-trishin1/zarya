from __future__ import annotations

import logging

from aiogram import Bot

from app.config import get_settings
from app.models.event import Event
from app.models.user import User
from app.utils.formatting import format_event_date

logger = logging.getLogger(__name__)

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
) -> tuple[int, int]:
    settings = get_settings()
    if not settings.bot_token_configured or not users:
        return 0, 0

    message = build_participant_broadcast_message(event, body)
    if len(message) > TELEGRAM_MESSAGE_LIMIT:
        message = message[: TELEGRAM_MESSAGE_LIMIT - 1] + "…"

    bot = Bot(token=settings.bot_token.strip())
    sent = 0
    failed = 0
    try:
        for user in users:
            try:
                await bot.send_message(user.telegram_id, message)
                sent += 1
            except Exception:
                failed += 1
                logger.exception(
                    "Failed to send broadcast to telegram_id=%s for event_id=%s",
                    user.telegram_id,
                    event.event_id,
                )
    finally:
        await bot.session.close()

    return sent, failed
