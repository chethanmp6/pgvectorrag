"""RAG API client for agent"""

import httpx
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RAGClient:
    """Client for interacting with RAG API"""
    
    def __init__(self, base_url: str):
        """
        Initialize RAG client
        
        Args:
            base_url: Base URL of RAG API (e.g., http://localhost:8000)
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def list_corpus(self) -> List[Dict]:
        """
        Get all available corpus
        
        Returns:
            List of corpus dictionaries with id, name, description
        """
        try:
            response = await self.client.get(f"{self.base_url}/corpus")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error listing corpus: {e}")
            raise
    
    async def get_corpus(self, corpus_id: str) -> Dict:
        """
        Get corpus details
        
        Args:
            corpus_id: UUID of the corpus
            
        Returns:
            Corpus dictionary with details
        """
        try:
            response = await self.client.get(f"{self.base_url}/corpus/{corpus_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting corpus {corpus_id}: {e}")
            raise
    
    async def search(
        self, 
        corpus_id: str, 
        query: str, 
        top_k: int = 5
    ) -> Dict:
        """
        Perform semantic search in a corpus
        
        Args:
            corpus_id: UUID of the corpus to search
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            Dictionary with query, results, and total_results
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/corpus/{corpus_id}/query",
                json={"query": query, "top_k": top_k}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error searching corpus {corpus_id}: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
