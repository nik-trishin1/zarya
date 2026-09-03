from __future__ import annotations

import html
import logging
import re

from aiogram import Bot
from aiogram.enums import ParseMode

from app.bot.keyboards import application_decision_keyboard

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
        return "@" + user.username
    display_name = (user.first_name or "Участник").strip()
    return html.escape(display_name)


def build_admin_registration_message(
    user: User,
    event: Event,
    reg_count: int,
    *,
    registered: bool,
    party_size: int = 1,
) -> str:
    mention = format_user_mention(user)
    event_name = html.escape(event.name)
    date_str = html.escape(format_event_date(event.date, event.time))
    if not registered:
        action = "отменил(а) регистрацию на"
    elif party_size > 1:
        action = f"будет на (+{party_size - 1})"
    else:
        action = "будет на"
    return (
        f"{mention} {action} <b>{event_name}</b> <b>{date_str}</b>\n"
        f"Всего гостей: {reg_count}"
    )


def build_admin_application_message(
    user: User,
    event: Event,
    reg_count: int,
    *,
    party_size: int = 1,
) -> str:
    mention = format_user_mention(user)
    event_name = html.escape(event.name)
    date_str = html.escape(format_event_date(event.date, event.time))
    return (
        f"{mention} подал(а) заявку на <b>{event_name}</b> <b>{date_str}</b>\n"
        f"Гостей в заявке: {party_size}\n"
        f"Всего гостей: {reg_count}"
    )


def build_user_approval_message(event: Event) -> str:
    date_str = format_event_date(event.date, event.time)
    return f"Ваше участие на {event.name} · {date_str} подтверждено!"


def build_user_rejection_message(event: Event) -> str:
    return f"Заявку на {event.name} не подтвердили."


async def notify_admins_registration_change(
    user: User,
    event: Event,
    reg_count: int,
    *,
    registered: bool,
    party_size: int = 1,
) -> None:
    settings = get_settings()
    admin_ids = settings.admin_ids
    if not admin_ids or not settings.bot_token_configured:
        return

    message = build_admin_registration_message(
        user,
        event,
        reg_count,
        registered=registered,
        party_size=party_size,
    )
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
                    parse_mode=ParseMode.HTML,
                )
    finally:
        await bot.session.close()


async def notify_admins_application(
    user: User,
    event: Event,
    reg_count: int,
    *,
    party_size: int = 1,
) -> None:
    settings = get_settings()
    admin_ids = settings.admin_ids
    if not admin_ids or not settings.bot_token_configured:
        return

    message = build_admin_application_message(
        user, event, reg_count, party_size=party_size
    )
    markup = application_decision_keyboard(event.event_id, user.user_id)
    bot = Bot(token=settings.bot_token.strip())
    context = f"admin_application_notify event_id={event.event_id}"
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
                    parse_mode=ParseMode.HTML,
                    reply_markup=markup,
                )
    finally:
        await bot.session.close()


async def notify_user_application_decision(
    user: User,
    event: Event,
    *,
    accepted: bool,
) -> None:
    settings = get_settings()
    if not settings.bot_token_configured:
        return
    message = (
        build_user_approval_message(event) if accepted else build_user_rejection_message(event)
    )
    bot = Bot(token=settings.bot_token.strip())
    context = f"user_application_decision event_id={event.event_id} accepted={accepted}"
    try:
        async with async_session() as db:
            await deliver_bot_message(
                bot,
                db,
                user.telegram_id,
                message,
                user=user,
                context=context,
            )
    finally:
        await bot.session.close()
