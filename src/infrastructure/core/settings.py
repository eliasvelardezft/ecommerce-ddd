import logging
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Settings
    api_title: str = "E-Commerce DDD API"
    api_version: str = "1.0.0"
    api_debug: bool = False
    api_description: str = "Domain-Driven Design e-commerce platform with CQRS and Event Sourcing"

    # Additional API settings
    api_contact_name: str = "Elias Velardez"
    api_contact_email: str = "eliasvelardez38@gmail.com"
    api_contact_url: str = "https://github.com/eliasvelardezft/ecommerce-ddd"
    api_license_name: str = "MIT License"
    api_license_url: str = "https://opensource.org/licenses/MIT"

    # Database Settings - PostgreSQL (primary)
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str

    # Legacy SQLite Settings (for backward compatibility)
    sqlite_url: str = "sqlite+aiosqlite:///:memory:"

    # MongoDB Settings
    mongo_url: str
    mongo_db: str

    @property
    def postgres_url(self) -> str:
        """Construct PostgreSQL async connection URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def postgres_sync_url(self) -> str:
        """Construct PostgreSQL sync connection URL for migrations"""
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Disable MongoDB logs
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("motor").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
