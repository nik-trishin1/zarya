from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    def admin_ids(self) -> set[int]:
        if not self.admin_telegram_ids.strip():
            return set()
        return {int(x.strip()) for x in self.admin_telegram_ids.split(",") if x.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
