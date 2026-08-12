from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Bot
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.bot.keyboards import maybe_ping_keyboard
from app.database import async_session
from app.models.event import Event
from app.models.maybe_ping import RegistrationMaybePing
from app.models.registration import Registration, RegistrationStatus
from app.models.user import User
from app.services.telegram_delivery import DeliveryOutcome, deliver_bot_message
from app.utils.calendar import event_start_datetime
from app.utils.formatting import format_event_date

logger = logging.getLogger(__name__)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")
MAYBE_PING_INTERVAL_SECONDS = 3600
SCHEDULER_ACTIVE_HOUR_START = 8
SCHEDULER_ACTIVE_HOUR_END = 22
DUE_WINDOW = timedelta(hours=1)

# (offset_id, timedelta before event_start)
MAYBE_PING_OFFSETS: tuple[tuple[str, timedelta], ...] = (
    ("7d", timedelta(days=7)),
    ("3d", timedelta(days=3)),
    ("2d", timedelta(days=2)),
    ("24h", timedelta(hours=24)),
)


def is_scheduler_active_hour(now: datetime) -> bool:
    local = now.astimezone(MOSCOW_TZ)
    return SCHEDULER_ACTIVE_HOUR_START <= local.hour <= SCHEDULER_ACTIVE_HOUR_END


def build_maybe_ping_schedule(
    event_start: datetime,
    now: datetime,
) -> list[tuple[str, datetime]]:
    """Return future (offset_id, due_at) pairs still after now."""
    entries: list[tuple[str, datetime]] = []
    for offset_id, delta in MAYBE_PING_OFFSETS:
        due_at = event_start - delta
        if due_at > now:
            entries.append((offset_id, due_at))
    return entries


def ping_is_due(due_at: datetime, now: datetime) -> bool:
    if due_at > now + DUE_WINDOW:
        return False
    return due_at >= now - DUE_WINDOW


def build_maybe_ping_message(event: Event) -> str:
    when = format_event_date(event.date, event.time)
    return (
        "Вы ещё думаете про это событие?\n"
        f"📌 {event.name} · {when}\n"
        f"📍 {event.location}"
    )


async def clear_maybe_pings(db: AsyncSession, registration_id: int) -> None:
    await db.execute(
        delete(RegistrationMaybePing).where(
            RegistrationMaybePing.registration_id == registration_id
        )
    )


async def rebuild_maybe_ping_schedule(
    db: AsyncSession,
    registration: Registration,
    event: Event,
    *,
    now: datetime | None = None,
) -> list[RegistrationMaybePing]:
    """Replace schedule with remaining future offsets. Caller commits."""
    await clear_maybe_pings(db, registration.registration_id)
    now = now or datetime.now(MOSCOW_TZ)
    start = event_start_datetime(event)
    rows: list[RegistrationMaybePing] = []
    for offset_id, due_at in build_maybe_ping_schedule(start, now):
        row = RegistrationMaybePing(
            registration_id=registration.registration_id,
            offset_id=offset_id,
            due_at=due_at,
        )
        db.add(row)
        rows.append(row)
    await db.flush()
    return rows


async def get_due_maybe_pings(db: AsyncSession, now: datetime) -> list[RegistrationMaybePing]:
    result = await db.execute(
        select(RegistrationMaybePing)
        .options(
            selectinload(RegistrationMaybePing.registration).selectinload(Registration.user),
            selectinload(RegistrationMaybePing.registration).selectinload(Registration.event),
        )
        .where(RegistrationMaybePing.sent_at.is_(None))
        .order_by(RegistrationMaybePing.due_at.asc())
    )
    pings = list(result.scalars().all())
    due: list[RegistrationMaybePing] = []
    for ping in pings:
        reg = ping.registration
        if reg is None or reg.status != RegistrationStatus.MAYBE.value:
            continue
        event = reg.event
        if event is None:
            continue
        if not ping_is_due(ping.due_at, now):
            continue
        due.append(ping)
    return due


async def process_due_maybe_pings(bot: Bot, *, now: datetime | None = None) -> int:
    now = now or datetime.now(MOSCOW_TZ)
    if not is_scheduler_active_hour(now):
        return 0

    sent_count = 0
    async with async_session() as db:
        pings = await get_due_maybe_pings(db, now)
        for ping in pings:
            reg = ping.registration
            user: User = reg.user
            event: Event = reg.event
            message = build_maybe_ping_message(event)
            outcome = await deliver_bot_message(
                bot,
                db,
                user.telegram_id,
                message,
                user=user,
                context=f"maybe_ping event_id={event.event_id} offset={ping.offset_id}",
                reply_markup=maybe_ping_keyboard(event.event_id),
            )
            ping.sent_at = now
            if outcome == DeliveryOutcome.SENT:
                sent_count += 1
        if pings:
            await db.commit()
    return sent_count


async def run_maybe_ping_scheduler() -> None:
    from aiogram import Bot

    from app.config import get_settings

    settings = get_settings()
    if not settings.bot_token_configured:
        return

    bot = Bot(token=settings.bot_token.strip())
    logger.info(
        "Maybe-ping scheduler started (every %ss, active %s:00–%s:00 MSK)",
        MAYBE_PING_INTERVAL_SECONDS,
        SCHEDULER_ACTIVE_HOUR_START,
        SCHEDULER_ACTIVE_HOUR_END,
    )
    try:
        while True:
            try:
                count = await process_due_maybe_pings(bot)
                if count:
                    logger.info("Maybe-ping scheduler sent %s message(s)", count)
            except Exception:
                logger.exception("Maybe-ping scheduler tick failed")
            await asyncio.sleep(MAYBE_PING_INTERVAL_SECONDS)
    finally:
        await bot.session.close()
