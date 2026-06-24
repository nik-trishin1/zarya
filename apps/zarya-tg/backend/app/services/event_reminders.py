from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import reminder_cancel_keyboard
from app.config import get_settings
from app.database import async_session
from app.models.event import Event
from app.services.events import get_event_registered_users
from app.services.telegram_delivery import DeliveryOutcome, deliver_bot_message
from app.utils.calendar import event_start_datetime
from app.utils.formatting import format_event_date

logger = logging.getLogger(__name__)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")
REMINDER_INTERVAL_SECONDS = 3600
REMINDER_WINDOW_START = timedelta(hours=23)
REMINDER_WINDOW_END = timedelta(hours=25)
SCHEDULER_ACTIVE_HOUR_START = 8
SCHEDULER_ACTIVE_HOUR_END = 22


def is_scheduler_active_hour(now: datetime) -> bool:
    local = now.astimezone(MOSCOW_TZ)
    return SCHEDULER_ACTIVE_HOUR_START <= local.hour <= SCHEDULER_ACTIVE_HOUR_END


def event_is_in_reminder_window(event: Event, now: datetime) -> bool:
    start = event_start_datetime(event)
    if start <= now:
        return False
    delta = start - now
    return REMINDER_WINDOW_START <= delta <= REMINDER_WINDOW_END


def build_reminder_message(event: Event) -> str:
    when = format_event_date(event.date, event.time)
    return (
        "Ждем вас уже завтра!\n"
        f"📌 {event.name} · {when}\n"
        f"📍 {event.location}\n"
        "До скорой встречи! ❤️"
    )


async def get_events_pending_reminder(db: AsyncSession, now: datetime) -> list[Event]:
    today = now.astimezone(MOSCOW_TZ).date()
    result = await db.execute(
        select(Event).where(
            Event.reminder_sent_at.is_(None),
            Event.date >= today,
        )
    )
    events = list(result.scalars().all())
    return [event for event in events if event_is_in_reminder_window(event, now)]


async def send_event_reminders(
    bot: Bot,
    db: AsyncSession,
    event: Event,
    *,
    reply_markup,
) -> tuple[int, int, int]:
    users = await get_event_registered_users(db, event.event_id)
    message = build_reminder_message(event)
    context = f"event_reminder event_id={event.event_id}"
    sent = 0
    blocked = 0
    failed = 0

    for user in users:
        outcome = await deliver_bot_message(
            bot,
            db,
            user.telegram_id,
            message,
            user=user,
            context=context,
            reply_markup=reply_markup,
        )
        if outcome == DeliveryOutcome.SENT:
            sent += 1
        elif outcome == DeliveryOutcome.BLOCKED:
            blocked += 1
        else:
            failed += 1

    return sent, blocked, failed


async def process_due_reminders(bot: Bot, now: datetime | None = None) -> int:
    """Send 24h reminders for due events. Returns number of events processed."""
    if now is None:
        now = datetime.now(MOSCOW_TZ)
    else:
        now = now.astimezone(MOSCOW_TZ)

    if not is_scheduler_active_hour(now):
        return 0

    processed = 0
    async with async_session() as db:
        events = await get_events_pending_reminder(db, now)
        for event in events:
            keyboard = reminder_cancel_keyboard(event.event_id)
            sent, blocked, failed = await send_event_reminders(
                bot,
                db,
                event,
                reply_markup=keyboard,
            )
            event.reminder_sent_at = now
            processed += 1
            logger.info(
                "Event reminder sent: event_id=%s sent=%s blocked=%s failed=%s",
                event.event_id,
                sent,
                blocked,
                failed,
            )
        if events:
            await db.commit()

    return processed


async def run_reminder_scheduler() -> None:
    settings = get_settings()
    if not settings.bot_token_configured:
        return

    bot = Bot(token=settings.bot_token.strip())
    logger.info(
        "Event reminder scheduler started (every %ss, active %s:00–%s:00 MSK)",
        REMINDER_INTERVAL_SECONDS,
        SCHEDULER_ACTIVE_HOUR_START,
        SCHEDULER_ACTIVE_HOUR_END,
    )
    try:
        while True:
            try:
                count = await process_due_reminders(bot)
                if count:
                    logger.info("Reminder scheduler processed %s event(s)", count)
            except Exception:
                logger.exception("Reminder scheduler tick failed")
            await asyncio.sleep(REMINDER_INTERVAL_SECONDS)
    finally:
        await bot.session.close()
