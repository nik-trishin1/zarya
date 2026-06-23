from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import events, registrations
from app.config import get_settings
from app.database import Base, engine
from app.services.storage import ensure_upload_dir

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_upload_dir()
    last_error: Exception | None = None
    for attempt in range(1, 6):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except Exception as exc:
            last_error = exc
            logger.warning("Database not ready (attempt %s/5): %s", attempt, exc)
            await asyncio.sleep(2)
    else:
        raise RuntimeError("Could not connect to database") from last_error
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="zarya API", version="1.0.0", lifespan=lifespan)

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if origins != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(events.router, prefix="/api")
    app.include_router(registrations.router, prefix="/api")

    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
