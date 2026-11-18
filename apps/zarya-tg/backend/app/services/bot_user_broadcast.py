from __future__ import annotations

from app.models.user import User
from app.services.participant_broadcast import validate_broadcast_body
from app.services.telegram_delivery import send_configured_bot_broadcast

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
    return await send_configured_bot_broadcast(
        users,
        body.strip(),
        context="bot_user_broadcast",
    )
