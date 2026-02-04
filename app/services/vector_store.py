from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Dict, Optional
from uuid import UUID
import json

from app.models import DocumentChunk, File
from app.services.embeddings import EmbeddingService


class VectorStoreService:
    """Service for managing vector storage and similarity search"""
    
    def __init__(self):
        """Initialize vector store service"""
        self.embedding_service = EmbeddingService()
    
    async def store_chunks(
        self,
        db: AsyncSession,
        chunks: List[Dict],
        file_id: UUID,
        corpus_id: UUID
    ) -> int:
        """
        Store document chunks with embeddings in database
        
        Args:
            db: Database session
            chunks: List of chunk dictionaries with text and metadata
            file_id: ID of the file these chunks belong to
            corpus_id: ID of the corpus
            
        Returns:
            Number of chunks stored
        """
        if not chunks:
            return 0
        
        # Extract texts for batch embedding generation
        texts = [chunk["chunk_text"] for chunk in chunks]
        
        # Generate embeddings in batch
        embeddings = await self.embedding_service.generate_embeddings_batch(texts)
        
        # Create DocumentChunk objects
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            chunk_obj = DocumentChunk(
                file_id=file_id,
                corpus_id=corpus_id,
                chunk_text=chunk["chunk_text"],
                chunk_index=chunk["chunk_index"],
                embedding=embeddings[i],
                extra_metadata=chunk.get("metadata", {})
            )
            chunk_objects.append(chunk_obj)
        
        # Bulk insert
        db.add_all(chunk_objects)
        await db.commit()
        
        return len(chunk_objects)
    
    async def similarity_search(
        self,
        db: AsyncSession,
        query: str,
        corpus_id: UUID,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Perform similarity search in vector database
        
        Args:
            db: Database session
            query: Search query text
            corpus_id: ID of corpus to search in
            top_k: Number of results to return
            
        Returns:
            List of search results with similarity scores
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_query_embedding(query)
        
        # Perform similarity search using cosine distance
        # Note: pgvector uses <=> for cosine distance (lower is more similar)
        query_stmt = (
            select(
                DocumentChunk.chunk_text,
                DocumentChunk.chunk_index,
                DocumentChunk.file_id,
                DocumentChunk.extra_metadata,
                File.filename,
                DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
            )
            .join(File, DocumentChunk.file_id == File.id)
            .where(DocumentChunk.corpus_id == corpus_id)
            .order_by("distance")
            .limit(top_k)
        )
        
        result = await db.execute(query_stmt)
        rows = result.all()
        
        # Convert to result dictionaries
        results = []
        for row in rows:
            # Convert distance to similarity score (1 - distance for cosine)
            similarity_score = 1 - row.distance
            
            results.append({
                "chunk_text": row.chunk_text,
                "similarity_score": similarity_score,
                "file_id": row.file_id,
                "filename": row.filename,
                "chunk_index": row.chunk_index,
                "metadata": row.extra_metadata
            })
        
        return results
    
    async def delete_file_chunks(self, db: AsyncSession, file_id: UUID) -> int:
        """
        Delete all chunks for a specific file
        
        Args:
            db: Database session
            file_id: ID of the file
            
        Returns:
            Number of chunks deleted
        """
        # Count chunks before deletion
        count_stmt = select(func.count(DocumentChunk.id)).where(DocumentChunk.file_id == file_id)
        result = await db.execute(count_stmt)
        count = result.scalar()
        
        # Delete chunks (will be handled by CASCADE, but explicit is better)
        delete_stmt = delete(DocumentChunk).where(DocumentChunk.file_id == file_id)
        await db.execute(delete_stmt)
        await db.commit()
        
        return count
    
    async def get_chunk_count(self, db: AsyncSession, file_id: UUID) -> int:
        """
        Get number of chunks for a file
        
        Args:
            db: Database session
            file_id: ID of the file
            
        Returns:
            Number of chunks
        """
        stmt = select(func.count(DocumentChunk.id)).where(DocumentChunk.file_id == file_id)
        result = await db.execute(stmt)
        return result.scalar()
