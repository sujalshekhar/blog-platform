import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the backend project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = Field(default="Blog Platform API")
    APP_VERSION: str = Field(default="0.1.0")

    # Database Settings
    DATABASE_URL: str = Field(default="postgresql://blog_user:blog_password@localhost:5432/blog_db")

    # JWT Settings
    JWT_SECRET: str = Field(default="super-secret-jwt-key-change-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

settings = Settings()
