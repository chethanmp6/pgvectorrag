import litellm
from typing import List
from app.config import settings


class EmbeddingService:
    """Service for generating embeddings using LiteLLM SDK with proxy"""
    
    def __init__(self):
        """Initialize LiteLLM embedding service"""
        # Use litellm_proxy/ prefix for proxy routing
        self.model = f"litellm_proxy/{settings.litellm_embedding_model}"
        self.api_key = settings.litellm_api_key
        self.api_base = settings.litellm_base_url
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
            response = await litellm.aembedding(
                model=self.model,
                input=[text],
                api_base=self.api_base,
                api_key=self.api_key
            )
            return response.data[0]['embedding']
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
                response = await litellm.aembedding(
                    model=self.model,
                    input=batch,
                    api_base=self.api_base,
                    api_key=self.api_key
                )
                
                # Extract embeddings in order
                batch_embeddings = [item['embedding'] for item in response.data]
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
