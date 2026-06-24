from __future__ import annotations

import logging
import re

from aiogram import Bot
from aiogram.enums import ParseMode

from app.config import get_settings
from app.database import async_session
from app.models.event import Event
from app.models.user import User
from app.services.telegram_delivery import deliver_bot_message
from app.services.users import get_user_by_telegram_id
from app.utils.formatting import format_event_date

logger = logging.getLogger(__name__)

_MARKDOWN_ESCAPE_PATTERN = re.compile(r"([_*\[`])")


def escape_markdown(text: str) -> str:
    return _MARKDOWN_ESCAPE_PATTERN.sub(r"\\\1", text)


def format_user_mention(user: User) -> str:
    if user.username:
        return f"@{user.username}"
    display_name = (user.first_name or "Участник").strip()
    return escape_markdown(display_name)


def build_admin_registration_message(
    user: User,
    event: Event,
    reg_count: int,
    *,
    registered: bool,
) -> str:
    mention = format_user_mention(user)
    event_name = escape_markdown(event.name)
    date_str = escape_markdown(format_event_date(event.date, event.time))
    action = "будет на" if registered else "отменил(а) регистрацию на"
    return (
        f"{mention} {action} *{event_name}* *{date_str}*\n"
        f"Всего участников: {reg_count}"
    )


async def notify_admins_registration_change(
    user: User,
    event: Event,
    reg_count: int,
    *,
    registered: bool,
) -> None:
    settings = get_settings()
    admin_ids = settings.admin_ids
    if not admin_ids or not settings.bot_token_configured:
        return

    message = build_admin_registration_message(user, event, reg_count, registered=registered)
    bot = Bot(token=settings.bot_token.strip())
    context = f"admin_registration_notify event_id={event.event_id}"
    try:
        async with async_session() as db:
            for admin_id in admin_ids:
                admin_user = await get_user_by_telegram_id(db, admin_id)
                await deliver_bot_message(
                    bot,
                    db,
                    admin_id,
                    message,
                    user=admin_user,
                    context=context,
                    parse_mode=ParseMode.MARKDOWN,
                )
    finally:
        await bot.session.close()
