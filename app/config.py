import os
from functools import lru_cache
from ipaddress import IPv4Address
from pathlib import Path
from typing import Optional, List

from pydantic import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool
    PROJECT_NAME: str
    DESCRIPTION: str
    APP_HOST: IPv4Address
    APP_PORT: int
    VERSION: str
    ALLOWED_HOSTS: Optional[List[IPv4Address]]

    PRETRAINED_MODEL_CACHE_DIR: Path

    class Config:
        validate_assignment = True


@lru_cache
def get_settings():
    return Settings(_env_file=os.getenv('ENV_FILE', '../.env'))
