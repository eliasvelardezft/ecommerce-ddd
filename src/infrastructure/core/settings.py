from pydantic_settings import BaseSettings
from functools import lru_cache

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

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
