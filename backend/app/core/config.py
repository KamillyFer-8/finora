from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Finora API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://finora:finora_local@localhost:5432/finora"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    jwt_secret_key: str = "change-me-in-production-with-at-least-32-characters"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    password_reset_minutes: int = 30
    cookie_secure: bool = False
    upload_dir: Path = Path("uploads")
    max_attachment_bytes: int = 10_485_760

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: object) -> object:
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",")]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
