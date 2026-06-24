from __future__ import annotations

import asyncio
import logging
import os

import uvicorn

from app.bot.handlers import run_bot
from app.config import get_settings
from app.main import app
from app.services.event_reminders import run_reminder_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_port() -> int:
    return int(os.environ.get("PORT", "8000"))


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


async def main() -> None:
    settings = get_settings()
    port = get_port()
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)

    if settings.bot_token_configured:
        asyncio.create_task(run_bot_safe())
        asyncio.create_task(run_reminder_scheduler_safe())
        logger.info("Starting API on 0.0.0.0:%s (bot + reminder scheduler in background)", port)
    else:
        logger.warning(
            "BOT_TOKEN not configured — running API only (set a real token from @BotFather to enable bot)"
        )
        logger.info("Starting API on 0.0.0.0:%s", port)

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
