from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# File Schemas
class FileResponse(BaseModel):
    """Schema for file response"""
    id: UUID
    corpus_id: UUID
    filename: str
    file_size: Optional[int]
    mime_type: Optional[str]
    created_at: datetime
    chunk_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Corpus Schemas
class CorpusCreate(BaseModel):
    """Schema for creating a corpus"""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the corpus")
    description: Optional[str] = Field(None, description="Description of the corpus")


class CorpusResponse(BaseModel):
    """Schema for corpus response"""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    file_count: Optional[int] = 0
    files: List[FileResponse] = []
    
    class Config:
        from_attributes = True


# Query Schemas
class QueryRequest(BaseModel):
    """Schema for search query request"""
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(5, ge=1, le=100, description="Number of results to return")


class SearchResult(BaseModel):
    """Schema for individual search result"""
    chunk_text: str
    similarity_score: float
    file_id: UUID
    filename: str
    chunk_index: int
    metadata: Optional[dict] = None


class QueryResponse(BaseModel):
    """Schema for query response"""
    query: str
    results: List[SearchResult]
    total_results: int
