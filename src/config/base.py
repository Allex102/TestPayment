import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    API_KEY: str = os.getenv("API_KEY")

    model_config = SettingsConfigDict(
        env_file = ".env",
        extra = "ignore"
    )

class DBSettings(BaseSettings):
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

class RabbitMQSettings(BaseSettings):
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

db_settings = DBSettings()
rabbitmq_settings = RabbitMQSettings()
settings = Settings()