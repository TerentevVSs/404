import os
from functools import lru_cache
from ipaddress import IPv4Address
from pathlib import Path
from typing import Optional, List, Dict, Any

from pydantic import BaseSettings, PostgresDsn, validator, RedisDsn


class Settings(BaseSettings):
    DEBUG: bool
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    APP_PORT: int
    VERSION: str
    ALLOWED_HOSTS: Optional[List[IPv4Address]]

    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator('SQLALCHEMY_DATABASE_URI', pre=True)
    def assemble_database_uri(cls, v: Optional[str],
                              values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_HOST'),
            path=f"/{values.get('POSTGRES_DB') or ''}",
            port=f"{values.get('POSTGRES_PORT') or ''}",
        )

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str

    REDIS_URI: Optional[RedisDsn] = None

    @validator('REDIS_URI', pre=True)
    def assemble_redis_uri(cls, v: Optional[str],
                           values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return RedisDsn.build(
            scheme='redis',
            host=values.get('REDIS_HOST'),
            port=values.get('REDIS_PORT'),
            password=values.get('REDIS_PASSWORD'),
            path=f"/1",
        )

    CELERY_DBURI: Optional[PostgresDsn] = None

    @validator('CELERY_DBURI', pre=True)
    def assemble_celery_dburi(cls, v: Optional[str],
                                   values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql+psycopg2',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_HOST'),
            path=f"/{values.get('POSTGRES_DB') or ''}",
            port=f"{values.get('POSTGRES_PORT') or ''}",
        )

    PRETRAINED_MODEL_CACHE_DIR: Path

    class Config:
        validate_assignment = True


@lru_cache
def get_settings():
    return Settings(_env_file=os.getenv('ENV_FILE', '../.env'))
