from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

logger = logging.getLogger(__name__)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


class DeliveryOutcome(str, Enum):
    SENT = "sent"
    BLOCKED = "blocked"
    FAILED = "failed"


def is_bot_blocked_error(exc: BaseException) -> bool:
    if not isinstance(exc, TelegramForbiddenError):
        return False
    message = str(exc).lower()
    return "blocked by the user" in message or "bot was blocked" in message


def is_user_unreachable_error(exc: BaseException) -> bool:
    if not isinstance(exc, TelegramForbiddenError):
        return False
    message = str(exc).lower()
    return is_bot_blocked_error(exc) or "user is deactivated" in message


async def mark_user_bot_blocked(db: AsyncSession, user: User) -> None:
    now = datetime.now(MOSCOW_TZ)
    if user.bot_blocked_at is None:
        user.bot_blocked_at = now
        await db.commit()
        logger.warning(
            "User blocked bot (recorded): user_id=%s telegram_id=%s username=%s first_name=%s",
            user.user_id,
            user.telegram_id,
            user.username,
            user.first_name,
        )


async def clear_user_bot_blocked(db: AsyncSession, user: User) -> None:
    if user.bot_blocked_at is not None:
        user.bot_blocked_at = None
        await db.commit()
        logger.info(
            "User unblocked bot (cleared): user_id=%s telegram_id=%s username=%s",
            user.user_id,
            user.telegram_id,
            user.username,
        )


async def deliver_bot_message(
    bot: Bot,
    db: AsyncSession | None,
    chat_id: int,
    text: str,
    *,
    user: User | None = None,
    context: str,
    parse_mode: str | None = None,
) -> DeliveryOutcome:
    try:
        await bot.send_message(chat_id, text, parse_mode=parse_mode)
    except Exception as exc:
        if user is not None and db is not None and is_bot_blocked_error(exc):
            await mark_user_bot_blocked(db, user)
            return DeliveryOutcome.BLOCKED
        if is_user_unreachable_error(exc):
            logger.warning(
                "Telegram user unreachable: chat_id=%s user_id=%s context=%s error=%s",
                chat_id,
                user.user_id if user else None,
                context,
                exc,
            )
            return DeliveryOutcome.FAILED
        logger.exception(
            "Failed to send Telegram message: chat_id=%s user_id=%s context=%s",
            chat_id,
            user.user_id if user else None,
            context,
        )
        return DeliveryOutcome.FAILED

    if user is not None and db is not None:
        await clear_user_bot_blocked(db, user)
    return DeliveryOutcome.SENT


async def deliver_bot_messages_to_users(
    bot: Bot,
    users: list[User],
    text: str,
    *,
    context: str,
    parse_mode: str | None = None,
) -> tuple[int, int, int]:
    """Returns (sent_count, blocked_count, other_failed_count)."""
    sent = 0
    blocked = 0
    failed = 0
    async with async_session() as db:
        for user in users:
            outcome = await deliver_bot_message(
                bot,
                db,
                user.telegram_id,
                text,
                user=user,
                context=context,
                parse_mode=parse_mode,
            )
            if outcome == DeliveryOutcome.SENT:
                sent += 1
            elif outcome == DeliveryOutcome.BLOCKED:
                blocked += 1
            else:
                failed += 1
    return sent, blocked, failed
