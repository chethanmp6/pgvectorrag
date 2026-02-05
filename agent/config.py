"""Configuration for RAG search agent"""

from pydantic_settings import BaseSettings
from typing import Optional


class AgentConfig(BaseSettings):
    """Agent configuration settings"""
    
    # RAG API
    rag_api_base_url: str = "http://localhost:8000"
    default_corpus_id: Optional[str] = None
    default_top_k: int = 5
    
    # LiteLLM Proxy (same as RAG embeddings)
    litellm_base_url: str = "http://localhost:4000/v1"
    litellm_api_key: str = "sk-3cPU913F4530vHZvmpxOWA"
    litellm_chat_model: str = "gpt-3.5-turbo"
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
