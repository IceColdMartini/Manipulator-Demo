"""
Configuration management for ManipulatorAI
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "ManipulatorAI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"

    # FastAPI Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # MongoDB Settings
    MONGODB_URL: str
    MONGODB_DB: str

    # Redis Settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0

    # Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str

    # Social Media Webhooks
    FACEBOOK_VERIFY_TOKEN: str
    FACEBOOK_APP_SECRET: str
    INSTAGRAM_VERIFY_TOKEN: str
    INSTAGRAM_APP_SECRET: str

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings instance
    """
    return Settings()
