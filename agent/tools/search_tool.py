"""
Search tool for RAG agent

This tool allows the agent to search the corpus directly without HTTP calls.
The corpus ID is configured in the environment.
"""

from typing import List, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import logging

from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class SearchTool:
    """Tool for searching RAG corpus"""
    
    def __init__(self, database_url: str, corpus_id: str):
        """
        Initialize search tool
        
        Args:
            database_url: Database connection string
            corpus_id: Default corpus ID to search
        """
        self.database_url = database_url
        self.corpus_id = UUID(corpus_id)
        
        # Create async engine with connection pooling
        self.engine = create_async_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False
        )
        
        # Create session factory
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Initialize vector store service
        self.vector_store = VectorStoreService()
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search the corpus for relevant documents
        
        Args:
            query: Search query text
            top_k: Number of results to return (default: 5)
            
        Returns:
            List of search results with chunk_text, similarity_score, filename, etc.
        """
        try:
            async with self.async_session() as session:
                results = await self.vector_store.similarity_search(
                    db=session,
                    query=query,
                    corpus_id=self.corpus_id,
                    top_k=top_k
                )
                return results
        except Exception as e:
            logger.error(f"Error searching corpus: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("Search tool database connections closed")
