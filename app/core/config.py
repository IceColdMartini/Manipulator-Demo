from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "ManipulatorAI"
    app_version: str = "0.1.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    app_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "development-secret-key"
    
    # Database Configuration
    postgresql_url: str = "postgresql://postgres:secure_password@localhost:5432/manipulator_ai"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "manipulator_ai"
    postgres_user: str = "postgres"
    postgres_password: str = "secure_password"
    
    mongodb_url: str = "mongodb://localhost:27017/manipulator_conversations"
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "manipulator_conversations"
    mongo_root_user: str = "admin"
    mongo_root_password: str = "secure_password"
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # OpenAI Configuration
    openai_api_key: str = "sk-test-key"
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str = "your_azure_openai_api_key_here"
    azure_openai_endpoint: str = "https://your-resource.openai.azure.com/"
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: str = "your_deployment_name_here"
    
    # Social Media Webhooks
    facebook_verify_token: str = "default_facebook_token"
    instagram_verify_token: str = "default_instagram_token"
    
    # Celery Configuration
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    
    # Flower Configuration
    flower_user: str = "admin"
    flower_password: str = "secure_password"
    
    # CORS and Security Configuration
    cors_origins: list = ["*"]
    allowed_hosts: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

# Global settings instance
settings = Settings()
