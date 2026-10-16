from __future__ import annotations

import logging
import os

import uvicorn

from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_port() -> int:
    return int(os.environ.get("PORT", "8000"))


if __name__ == "__main__":
    port = get_port()
    logger.info("Starting link-qr on 0.0.0.0:%s", port)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
