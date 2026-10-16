from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./link_qr.db"
    admin_token: str = "change-me"
    public_base_url: str = "http://localhost:8000"
    cookie_name: str = "link_qr_admin"
    cookie_max_age_seconds: int = 60 * 60 * 24 * 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
