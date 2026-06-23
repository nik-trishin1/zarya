from __future__ import annotations

import re
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

_BOT_TOKEN_PLACEHOLDERS = {
    "",
    "your-telegram-bot-token",
    "your-bot-token",
    "changeme",
    "change-me",
}
_BOT_TOKEN_PATTERN = re.compile(r"^\d+:[A-Za-z0-9_-]+$")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./zarya.db"
    bot_token: str = ""
    admin_telegram_ids: str = ""
    webapp_url: str = "http://localhost:5173"
    api_base_url: str = "http://localhost:8000"
    upload_dir: str = "./uploads"
    cors_origins: str = "*"
    secret_key: str = "change-me-in-production"
    dev_mode: bool = False

    @property
    def bot_token_configured(self) -> bool:
        token = self.bot_token.strip()
        if token.lower() in _BOT_TOKEN_PLACEHOLDERS:
            return False
        return bool(_BOT_TOKEN_PATTERN.match(token))

    @property
    def allow_browser_dev(self) -> bool:
        """Allow API access from a regular browser without Telegram initData."""
        if self.dev_mode:
            return True
        # Local SQLite setup without a bot — typical `dev-local.sh` workflow
        return not self.bot_token_configured and self.database_url.startswith("sqlite")

    @property
    def admin_ids(self) -> set[int]:
        if not self.admin_telegram_ids.strip():
            return set()
        return {int(x.strip()) for x in self.admin_telegram_ids.split(",") if x.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
