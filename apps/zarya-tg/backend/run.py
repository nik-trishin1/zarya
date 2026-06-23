from __future__ import annotations

import asyncio
import logging

import uvicorn

from app.bot.handlers import run_bot
from app.config import get_settings
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    settings = get_settings()
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    if settings.bot_token_configured:
        await asyncio.gather(server.serve(), run_bot())
    else:
        logger.warning("BOT_TOKEN not configured — running API only (set a real token from @BotFather to enable bot)")
        await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
