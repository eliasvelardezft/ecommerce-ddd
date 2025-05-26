from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import logging


class Settings(BaseSettings):
    # API Settings
    api_title: str
    api_version: str
    api_debug: bool

    # SQLite Settings
    sqlite_url: str

    # MongoDB Settings
    mongo_url: str
    mongo_db: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Disable MongoDB logs
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("motor").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
