from sqlalchemy import Column, String, Text, BigInteger, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

from app.database import Base


class Corpus(Base):
    """Corpus model - represents a collection of documents"""
    __tablename__ = "corpus"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now())
    
    # Relationships
    files = relationship("File", back_populates="corpus", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="corpus", cascade="all, delete-orphan")


class File(Base):
    """File model - represents uploaded files in a corpus"""
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    corpus_id = Column(UUID(as_uuid=True), ForeignKey("corpus.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    
    # Relationships
    corpus = relationship("Corpus", back_populates="files")
    chunks = relationship("DocumentChunk", back_populates="file", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """DocumentChunk model - represents text chunks with embeddings"""
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    corpus_id = Column(UUID(as_uuid=True), ForeignKey("corpus.id", ondelete="CASCADE"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(768))  # Gemini text-embedding-004 dimension
    extra_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    
    # Relationships
    file = relationship("File", back_populates="chunks")
    corpus = relationship("Corpus", back_populates="chunks")
