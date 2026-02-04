from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Database
    database_url: str = "postgresql+asyncpg://raguser:ragpassword@localhost:5432/ragdb"
    
    # OpenAI
    openai_api_key: str
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Search
    default_top_k: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
