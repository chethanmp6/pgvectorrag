from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import Corpus, File, DocumentChunk
from app.schemas import CorpusCreate, CorpusResponse, FileResponse

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
    
    # Manually construct response to avoid lazy loading 'files' relationship
    return CorpusResponse(
        id=new_corpus.id,
        name=new_corpus.name,
        description=new_corpus.description,
        created_at=new_corpus.created_at,
        updated_at=new_corpus.updated_at,
        file_count=0,
        files=[]
    )


@router.get("", response_model=List[CorpusResponse])
async def list_corpus(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List all corpus with pagination, including files and counts
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of corpus with file details
    """
    # Query corpus
    stmt = select(Corpus).offset(skip).limit(limit)
    result = await db.execute(stmt)
    corpus_objs = result.scalars().all()
    
    # For each corpus, fetch files with chunk counts
    corpus_responses = []
    for corpus in corpus_objs:
        # Fetch files with chunk counts for this corpus
        files_stmt = (
            select(File, func.count(DocumentChunk.id).label("chunk_count"))
            .outerjoin(DocumentChunk, File.id == DocumentChunk.file_id)
            .where(File.corpus_id == corpus.id)
            .group_by(File.id)
        )
        files_result = await db.execute(files_stmt)
        files_rows = files_result.all()
        
        file_responses = []
        for row in files_rows:
            f = row[0]
            count = row[1]
            f_resp = FileResponse.model_validate(f)
            f_resp.chunk_count = count
            file_responses.append(f_resp)
        
        corpus_responses.append(CorpusResponse(
            id=corpus.id,
            name=corpus.name,
            description=corpus.description,
            created_at=corpus.created_at,
            updated_at=corpus.updated_at,
            file_count=len(file_responses),
            files=file_responses
        ))
    
    return corpus_responses


@router.get("/{corpus_id}", response_model=CorpusResponse)
async def get_corpus(
    corpus_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get corpus details by ID, including files and counts
    
    Args:
        corpus_id: Corpus ID
        db: Database session
        
    Returns:
        Corpus details with file details
    """
    # Query corpus
    stmt = select(Corpus).where(Corpus.id == corpus_id)
    result = await db.execute(stmt)
    corpus = result.scalar_one_or_none()
    
    if not corpus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Corpus with ID {corpus_id} not found"
        )
    
    # Fetch files with chunk counts
    files_stmt = (
        select(File, func.count(DocumentChunk.id).label("chunk_count"))
        .outerjoin(DocumentChunk, File.id == DocumentChunk.file_id)
        .where(File.corpus_id == corpus_id)
        .group_by(File.id)
    )
    files_result = await db.execute(files_stmt)
    files_rows = files_result.all()
    
    file_responses = []
    for row in files_rows:
        f = row[0]
        count = row[1]
        f_resp = FileResponse.model_validate(f)
        f_resp.chunk_count = count
        file_responses.append(f_resp)
    
    return CorpusResponse(
        id=corpus.id,
        name=corpus.name,
        description=corpus.description,
        created_at=corpus.created_at,
        updated_at=corpus.updated_at,
        file_count=len(file_responses),
        files=file_responses
    )


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
