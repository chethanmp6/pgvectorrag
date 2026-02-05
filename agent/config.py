"""Configuration for RAG search agent"""

from pydantic_settings import BaseSettings
from typing import Optional


class AgentConfig(BaseSettings):
    """Agent configuration settings"""
    
    # RAG API (for conversational agent)
    rag_api_base_url: str = "http://localhost:8000"
    
    # Database and Corpus (for search tool)
    database_url: str = "postgresql+asyncpg://litellm_user:litellm_secure_password_change_this@localhost:5432/ragdb"
    corpus_id: Optional[str] = None  # Corpus ID for search tool (optional)
    default_top_k: int = 5
    
    # LiteLLM Proxy (same as RAG embeddings)
    litellm_base_url: str = "http://localhost:4000/v1"
    litellm_api_key: str = "sk-3cPU913F4530vHZvmpxOWA"
    litellm_chat_model: str = "gemini-2.5-flash"
    litellm_embedding_model: str = "text-embedding-ada-002"
    
    # Agent behavior
    temperature: float = 0.7
    max_conversation_history: int = 10
    include_sources: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars from .env file


# Global config instance
config = AgentConfig()
