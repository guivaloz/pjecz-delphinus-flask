"""
Settings
"""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


def get_secret(secret_id: str, default: str = "") -> str:
    """Obtener el valor del secreto desde desde las variables de entorno"""
    value = os.getenv(secret_id.upper(), "")
    if value == "":
        return default
    return value


class Settings(BaseSettings):
    """Settings"""

    # Variables de entorno
    ESTADO_CLAVE: str = get_secret("ESTADO_CLAVE")
    MUNICIPIO_CLAVE: str = get_secret("MUNICIPIO_CLAVE")
    SALT: str = get_secret("SALT")
    SECRET_KEY: str = get_secret("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI: str = get_secret("SQLALCHEMY_DATABASE_URI")
    TZ: str = get_secret("TZ", "America/Mexico_City")

    class Config:
        """Load configuration"""

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            """Change the order of precedence of settings sources"""
            return env_settings, file_secret_settings, init_settings


@lru_cache()
def get_settings() -> Settings:
    """Get Settings"""
    return Settings()
