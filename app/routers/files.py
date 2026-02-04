from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID
import logging

from app.database import get_db
from app.models import Corpus, File, DocumentChunk
from app.schemas import FileResponse
from app.services.document_processor import DocumentProcessor
from app.services.chunking import ChunkingService
from app.services.vector_store import VectorStoreService

router = APIRouter(prefix="/corpus/{corpus_id}/files", tags=["Files"])
logger = logging.getLogger(__name__)


@router.post("", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    corpus_id: UUID,
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and process a file in a corpus
    
    Args:
        corpus_id: Corpus ID
        file: Uploaded file
        db: Database session
        
    Returns:
        File metadata and processing status
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
    
    # Validate file type
    allowed_extensions = ['pdf', 'docx', 'txt', 'md']
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_extension}' not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Extract text from file
        document_processor = DocumentProcessor()
        text = document_processor.extract_text(file_content, file.filename)
        
        if not text or not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text could be extracted from the file"
            )
        
        # Create file record
        mime_type = document_processor.get_mime_type(file.filename)
        new_file = File(
            corpus_id=corpus_id,
            filename=file.filename,
            file_size=file_size,
            mime_type=mime_type
        )
        
        db.add(new_file)
        await db.commit()
        await db.refresh(new_file)
        
        # Chunk the text
        chunking_service = ChunkingService()
        chunks = chunking_service.chunk_text(
            text,
            metadata={"filename": file.filename, "mime_type": mime_type}
        )
        
        logger.info(f"Created {len(chunks)} chunks for file {file.filename}")
        
        # Store chunks with embeddings
        vector_store = VectorStoreService()
        chunk_count = await vector_store.store_chunks(
            db=db,
            chunks=chunks,
            file_id=new_file.id,
            corpus_id=corpus_id
        )
        
        logger.info(f"Stored {chunk_count} chunks with embeddings for file {file.filename}")
        
        # Build response
        file_response = FileResponse.model_validate(new_file)
        file_response.chunk_count = chunk_count
        
        return file_response
        
    except ValueError as e:
        # Rollback if file was created but processing failed
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("", response_model=List[FileResponse])
async def list_files(
    corpus_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    List all files in a corpus
    
    Args:
        corpus_id: Corpus ID
        db: Database session
        
    Returns:
        List of files
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
    
    # Query files with chunk count
    stmt = (
        select(File, func.count(DocumentChunk.id).label("chunk_count"))
        .outerjoin(DocumentChunk, File.id == DocumentChunk.file_id)
        .where(File.corpus_id == corpus_id)
        .group_by(File.id)
        .order_by(File.created_at.desc())
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    # Build response
    files_list = []
    for row in rows:
        file = row[0]
        chunk_count = row[1]
        
        file_response = FileResponse.model_validate(file)
        file_response.chunk_count = chunk_count
        files_list.append(file_response)
    
    return files_list


@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
async def delete_file(
    corpus_id: UUID,
    file_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a file and all its vectors from the corpus
    
    Args:
        corpus_id: Corpus ID
        file_id: File ID
        db: Database session
        
    Returns:
        Success message
    """
    # Find file
    stmt = select(File).where(
        File.id == file_id,
        File.corpus_id == corpus_id
    )
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found in corpus {corpus_id}"
        )
    
    # Get chunk count before deletion
    chunk_count_stmt = select(func.count(DocumentChunk.id)).where(DocumentChunk.file_id == file_id)
    chunk_result = await db.execute(chunk_count_stmt)
    chunk_count = chunk_result.scalar()
    
    filename = file.filename
    
    # Delete file (CASCADE will handle chunks automatically)
    await db.delete(file)
    await db.commit()
    
    logger.info(f"Deleted file '{filename}' and {chunk_count} associated vectors")
    
    return {
        "message": f"File '{filename}' and {chunk_count} associated vectors deleted successfully",
        "file_id": str(file_id),
        "chunks_deleted": chunk_count
    }
