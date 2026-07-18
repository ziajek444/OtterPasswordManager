from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_prefix="OTTER_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Otter Password Manager API"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite+aiosqlite:///./data/otter_password_manager.db"

    log_level: str = "INFO"
    log_format: Literal["console", "json"] = "console"

    jwt_secret: str = Field(min_length=32)
    access_token_expire_minutes: int = Field(default=15, ge=1)
    refresh_token_expire_days: int = Field(default=30, ge=1)
    encryption_key: str

    uvicorn_host: str = "127.0.0.1"
    uvicorn_port: int = Field(default=8000, ge=1, le=65535)
    uvicorn_reload: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
