from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    env: str = "development"
    log_level: str = "INFO"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    gemini_api_key: SecretStr = SecretStr("")
    gemini_chat_model: str = "gemini-3.8-flash"
    gemini_parser_model: str = "gemini-3.5-flash-lite"
    gemini_embed_model: str = "gemini-embedding-001"

    saramin_access_key: SecretStr = SecretStr("")
    saramin_max_pages: int = 10

    admin_token: SecretStr = SecretStr("")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_dev(self) -> bool:
        return self.env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
