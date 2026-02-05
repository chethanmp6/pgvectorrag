from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Database
    database_url: str = "postgresql+asyncpg://raguser:ragpassword@localhost:5432/ragdb"
    
    # LiteLLM Proxy Configuration
    litellm_base_url: str = "http://localhost:4000/v1"
    litellm_api_key: str = "sk-3cPU913F4530vHZvmpxOWA"
    litellm_embedding_model: str = "text-embedding-ada-002"
    
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
        extra = "ignore"  # Ignore extra env vars (e.g., agent-specific vars)


# Global settings instance
settings = Settings()
