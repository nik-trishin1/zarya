from __future__ import annotations

import asyncio
import logging

from app.bot.handlers import run_bot
from app.config import get_settings
from app.services.event_reminders import run_reminder_scheduler

logger = logging.getLogger(__name__)

_background_tasks: list[asyncio.Task[None]] = []


async def run_bot_safe() -> None:
    try:
        await run_bot()
    except Exception:
        logger.exception("Telegram bot failed — API keeps running")


async def run_reminder_scheduler_safe() -> None:
    try:
        await run_reminder_scheduler()
    except Exception:
        logger.exception("Reminder scheduler failed — API keeps running")


def start_background_tasks() -> list[asyncio.Task[None]]:
    """Start bot polling and reminder scheduler after the database is ready."""
    settings = get_settings()
    if not settings.bot_token_configured:
        return []

    tasks = [
        asyncio.create_task(run_bot_safe(), name="telegram-bot"),
        asyncio.create_task(run_reminder_scheduler_safe(), name="reminder-scheduler"),
    ]
    _background_tasks.extend(tasks)
    logger.info("Background tasks started (bot + reminder scheduler)")
    return tasks


async def stop_background_tasks() -> None:
    for task in _background_tasks:
        task.cancel()
    if _background_tasks:
        await asyncio.gather(*_background_tasks, return_exceptions=True)
        _background_tasks.clear()
