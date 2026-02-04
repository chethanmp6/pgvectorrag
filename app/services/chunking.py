import tiktoken
from typing import List, Dict
from app.config import settings


class ChunkingService:
    """Service for chunking text into fixed-size pieces"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize chunking service
        
        Args:
            chunk_size: Number of tokens per chunk (default from settings)
            chunk_overlap: Number of overlapping tokens between chunks (default from settings)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        # Use cl100k_base encoding for OpenAI ada-002
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into fixed-size chunks with overlap
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of dictionaries containing chunk text, index, and metadata
        """
        if not text or not text.strip():
            return []
        
        # Encode text to tokens
        tokens = self.encoding.encode(text)
        
        chunks = []
        start_idx = 0
        chunk_index = 0
        
        while start_idx < len(tokens):
            # Get chunk of tokens
            end_idx = start_idx + self.chunk_size
            chunk_tokens = tokens[start_idx:end_idx]
            
            # Decode tokens back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Create chunk metadata
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                "token_count": len(chunk_tokens),
                "start_token": start_idx,
                "end_token": end_idx
            })
            
            chunks.append({
                "chunk_text": chunk_text,
                "chunk_index": chunk_index,
                "metadata": chunk_metadata
            })
            
            # Move to next chunk with overlap
            start_idx += self.chunk_size - self.chunk_overlap
            chunk_index += 1
        
        return chunks
    
    def count_tokens(self, text: str) -> int:
        """
        Count number of tokens in text
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))
