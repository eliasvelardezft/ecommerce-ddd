from pydantic_settings import BaseSettings
from functools import lru_cache
import logging
import colorlog

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

# Disable MongoDB logs
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("motor").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Create color formatter
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Get root logger
logger = colorlog.getLogger()
logger.setLevel(logging.INFO)

# Remove existing handlers
if logger.handlers:
    logger.handlers.clear()

# Add console handler with color formatter
handler = colorlog.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
