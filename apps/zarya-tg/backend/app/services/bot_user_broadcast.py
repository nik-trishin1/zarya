from __future__ import annotations

from aiogram import Bot

from app.config import get_settings
from app.models.user import User
from app.services.participant_broadcast import validate_broadcast_body
from app.services.telegram_delivery import deliver_bot_messages_to_users

TELEGRAM_MESSAGE_LIMIT = 4096

__all__ = [
    "build_bot_user_broadcast_preview",
    "send_bot_user_broadcast",
    "validate_broadcast_body",
]


def build_bot_user_broadcast_preview(body: str, recipient_count: int) -> str:
    message = body.strip()
    return (
        f"Проверьте сообщение. Получателей: {recipient_count}\n\n"
        f"———\n{message}\n———"
    )


async def send_bot_user_broadcast(
    users: list[User],
    body: str,
) -> tuple[int, int, int]:
    """Returns (sent_count, blocked_count, other_failed_count)."""
    settings = get_settings()
    if not settings.bot_token_configured or not users:
        return 0, 0, 0

    message = body.strip()
    if len(message) > TELEGRAM_MESSAGE_LIMIT:
        message = message[: TELEGRAM_MESSAGE_LIMIT - 1] + "…"

    bot = Bot(token=settings.bot_token.strip())
    context = "bot_user_broadcast"
    try:
        return await deliver_bot_messages_to_users(bot, users, message, context=context)
    finally:
        await bot.session.close()
