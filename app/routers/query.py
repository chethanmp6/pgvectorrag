from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models import Corpus
from app.schemas import QueryRequest, QueryResponse, SearchResult
from app.services.vector_store import VectorStoreService
from app.config import settings

router = APIRouter(prefix="/corpus/{corpus_id}/query", tags=["Query"])


@router.post("", response_model=QueryResponse)
async def search_corpus(
    corpus_id: UUID,
    query_data: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Perform semantic search in a corpus
    
    Args:
        corpus_id: Corpus ID
        query_data: Query request with search text and top_k
        db: Database session
        
    Returns:
        Search results with similarity scores
    """
    # Verify corpus exists
    corpus_stmt = select(Corpus).where(Corpus.id == corpus_id)
    corpus_result = await db.execute(corpus_stmt)
    corpus = corpus_result.scalar_one_or_none()
    
    if not corpus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Corpus with ID {corpus_id} not found"
        )
    
    try:
        # Perform similarity search
        vector_store = VectorStoreService()
        results = await vector_store.similarity_search(
            db=db,
            query=query_data.query,
            corpus_id=corpus_id,
            top_k=query_data.top_k
        )
        
        # Convert to SearchResult objects
        search_results = [
            SearchResult(
                chunk_text=result["chunk_text"],
                similarity_score=result["similarity_score"],
                file_id=result["file_id"],
                filename=result["filename"],
                chunk_index=result["chunk_index"],
                metadata=result.get("metadata")
            )
            for result in results
        ]
        
        return QueryResponse(
            query=query_data.query,
            results=search_results,
            total_results=len(search_results)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )
