from openai import AsyncOpenAI
from typing import List
import asyncio
from app.config import settings


class EmbeddingService:
    """Service for generating embeddings using LiteLLM proxy"""
    
    def __init__(self):
        """Initialize LiteLLM client (OpenAI-compatible)"""
        self.client = AsyncOpenAI(
            base_url=settings.litellm_base_url,
            api_key=settings.litellm_api_key
        )
        self.model = settings.litellm_embedding_model
        self.max_batch_size = 100  # Batch limit
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise ValueError(f"Error generating embedding: {str(e)}")
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = []
        
        # Process in batches to respect API limits
        for i in range(0, len(texts), self.max_batch_size):
            batch = texts[i:i + self.max_batch_size]
            
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                
                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
            except Exception as e:
                raise ValueError(f"Error generating batch embeddings: {str(e)}")
        
        return embeddings
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
        """
        return await self.generate_embedding(query)
