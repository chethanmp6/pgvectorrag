-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Corpus table
CREATE TABLE IF NOT EXISTS corpus (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Files table
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    corpus_id UUID NOT NULL REFERENCES corpus(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    mime_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_corpus FOREIGN KEY (corpus_id) REFERENCES corpus(id) ON DELETE CASCADE
);

-- Document chunks table with vector embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    corpus_id UUID NOT NULL REFERENCES corpus(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(768),  -- Gemini text-embedding-004 produces 768-dimensional vectors
    extra_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_file FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    CONSTRAINT fk_corpus_chunk FOREIGN KEY (corpus_id) REFERENCES corpus(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_files_corpus_id ON files(corpus_id);
CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON document_chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_chunks_corpus_id ON document_chunks(corpus_id);

-- Create vector similarity search index using IVFFlat
-- This index speeds up similarity searches using cosine distance
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_corpus_updated_at BEFORE UPDATE ON corpus
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
