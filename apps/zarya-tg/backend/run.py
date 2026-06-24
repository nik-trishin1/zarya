from __future__ import annotations

import asyncio
import logging
import os

import uvicorn

from app.config import get_settings
from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_port() -> int:
    return int(os.environ.get("PORT", "8000"))


async def main() -> None:
    settings = get_settings()
    port = get_port()
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)

    if not settings.bot_token_configured:
        logger.warning(
            "BOT_TOKEN not configured — running API only (set a real token from @BotFather to enable bot)"
        )

    logger.info("Starting API on 0.0.0.0:%s", port)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
