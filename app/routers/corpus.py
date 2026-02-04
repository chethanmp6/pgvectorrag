from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import Corpus
from app.schemas import CorpusCreate, CorpusResponse

router = APIRouter(prefix="/corpus", tags=["Corpus"])


@router.post("", response_model=CorpusResponse, status_code=status.HTTP_201_CREATED)
async def create_corpus(
    corpus_data: CorpusCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new corpus
    
    Args:
        corpus_data: Corpus creation data
        db: Database session
        
    Returns:
        Created corpus
    """
    # Create new corpus
    new_corpus = Corpus(
        name=corpus_data.name,
        description=corpus_data.description
    )
    
    db.add(new_corpus)
    await db.commit()
    await db.refresh(new_corpus)
    
    # Get file count (will be 0 for new corpus)
    response = CorpusResponse.model_validate(new_corpus)
    response.file_count = 0
    
    return response


@router.get("", response_model=List[CorpusResponse])
async def list_corpus(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List all corpus with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of corpus
    """
    # Query corpus with file count
    stmt = (
        select(Corpus, func.count(Corpus.files).label("file_count"))
        .outerjoin(Corpus.files)
        .group_by(Corpus.id)
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    # Build response
    corpus_list = []
    for row in rows:
        corpus = row[0]
        file_count = row[1]
        
        corpus_response = CorpusResponse.model_validate(corpus)
        corpus_response.file_count = file_count
        corpus_list.append(corpus_response)
    
    return corpus_list


@router.get("/{corpus_id}", response_model=CorpusResponse)
async def get_corpus(
    corpus_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get corpus details by ID
    
    Args:
        corpus_id: Corpus ID
        db: Database session
        
    Returns:
        Corpus details
    """
    # Query corpus with file count
    stmt = (
        select(Corpus, func.count(Corpus.files).label("file_count"))
        .outerjoin(Corpus.files)
        .where(Corpus.id == corpus_id)
        .group_by(Corpus.id)
    )
    
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Corpus with ID {corpus_id} not found"
        )
    
    corpus = row[0]
    file_count = row[1]
    
    corpus_response = CorpusResponse.model_validate(corpus)
    corpus_response.file_count = file_count
    
    return corpus_response


@router.delete("/{corpus_id}", status_code=status.HTTP_200_OK)
async def delete_corpus(
    corpus_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a corpus and all associated files and vectors
    
    Args:
        corpus_id: Corpus ID
        db: Database session
        
    Returns:
        Success message
    """
    # Find corpus
    stmt = select(Corpus).where(Corpus.id == corpus_id)
    result = await db.execute(stmt)
    corpus = result.scalar_one_or_none()
    
    if not corpus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Corpus with ID {corpus_id} not found"
        )
    
    # Delete corpus (CASCADE will handle files and chunks)
    await db.delete(corpus)
    await db.commit()
    
    return {
        "message": f"Corpus '{corpus.name}' and all associated data deleted successfully",
        "corpus_id": str(corpus_id)
    }
