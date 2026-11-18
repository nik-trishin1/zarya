from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from . import admin_menu, approvals, broadcast, common, event_create, event_edit, reminders
from .common import is_admin
from app.config import get_settings
from app.services.event_announcement import send_new_event_announcement

logger = logging.getLogger(__name__)

__all__ = [
    "create_dispatcher",
    "run_bot",
    "is_admin",
    "send_new_event_announcement",
]


def create_dispatcher() -> Dispatcher:
    """Include domain routers; order matches original handlers.py sections."""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    # Original single-router order by domain (non-overlapping filters):
    # start/myid → reminders/maybe → admin menu/manage/archive/delete → create → edit → approvals → broadcast
    dp.include_router(common.router)
    dp.include_router(reminders.router)
    dp.include_router(admin_menu.router)
    dp.include_router(event_create.router)
    dp.include_router(event_edit.router)
    dp.include_router(approvals.router)
    dp.include_router(broadcast.router)
    return dp


async def run_bot():
    settings = get_settings()
    if not settings.bot_token_configured:
        logger.warning("BOT_TOKEN not configured, bot will not start")
        return

    bot = Bot(token=settings.bot_token.strip())
    dp = create_dispatcher()
    logger.info("Telegram bot polling started (webapp_url=%s)", settings.webapp_url)
    await dp.start_polling(bot)
