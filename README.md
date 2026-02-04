# RAG System with PostgreSQL pgvector

A production-ready Retrieval-Augmented Generation (RAG) system built with FastAPI and PostgreSQL pgvector, similar to Google Vertex AI RAG Engine.

## Features

- 🗂️ **Corpus Management**: Create, list, retrieve, and delete document collections
- 📄 **Multi-Format Support**: PDF, DOCX, TXT, and Markdown files
- 🔍 **Semantic Search**: Vector similarity search using OpenAI embeddings
- 🚀 **Fast API**: High-performance async FastAPI backend
- 🐘 **PostgreSQL + pgvector**: Efficient vector storage and retrieval
- 🐳 **Docker Ready**: Easy deployment with Docker Compose

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│       FastAPI Application       │
│  ┌───────────────────────────┐  │
│  │  Corpus Management API    │  │
│  │  File Management API      │  │
│  │  Query/Search API         │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │  Document Processing      │  │
│  │  - Text Extraction        │  │
│  │  - Chunking (512 tokens)  │  │
│  │  - Embedding (ada-002)    │  │
│  └───────────────────────────┘  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  PostgreSQL + pgvector          │
│  - Corpus table                 │
│  - Files table                  │
│  - Document chunks (vectors)    │
└─────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenAI API key

### Setup

1. **Clone and navigate to the project**:
   ```bash
   cd /Users/apple/Documents/Virtusa/virtusavertexrag
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and add your OpenAI API key**:
   ```
   OPENAI_API_KEY=your-actual-api-key-here
   ```

4. **Start PostgreSQL with pgvector**:
   ```bash
   docker-compose up -d
   ```

5. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the application**:
   ```bash
   python -m app.main
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Corpus Management

- **Create Corpus**: `POST /corpus`
  ```bash
  curl -X POST http://localhost:8000/corpus \
    -H "Content-Type: application/json" \
    -d '{"name": "my_corpus", "description": "My document collection"}'
  ```

- **List Corpus**: `GET /corpus`
  ```bash
  curl http://localhost:8000/corpus
  ```

- **Get Corpus**: `GET /corpus/{corpus_id}`
  ```bash
  curl http://localhost:8000/corpus/{corpus_id}
  ```

- **Delete Corpus**: `DELETE /corpus/{corpus_id}`
  ```bash
  curl -X DELETE http://localhost:8000/corpus/{corpus_id}
  ```

### File Management

- **Upload File**: `POST /corpus/{corpus_id}/files`
  ```bash
  curl -X POST http://localhost:8000/corpus/{corpus_id}/files \
    -F "file=@document.pdf"
  ```

- **List Files**: `GET /corpus/{corpus_id}/files`
  ```bash
  curl http://localhost:8000/corpus/{corpus_id}/files
  ```

- **Delete File**: `DELETE /corpus/{corpus_id}/files/{file_id}`
  ```bash
  curl -X DELETE http://localhost:8000/corpus/{corpus_id}/files/{file_id}
  ```

### Search

- **Semantic Search**: `POST /corpus/{corpus_id}/query`
  ```bash
  curl -X POST http://localhost:8000/corpus/{corpus_id}/query \
    -H "Content-Type: application/json" \
    -d '{"query": "What is machine learning?", "top_k": 5}'
  ```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
virtusavertexrag/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   ├── corpus.py        # Corpus endpoints
│   │   ├── files.py         # File endpoints
│   │   └── query.py         # Search endpoints
│   └── services/
│       ├── document_processor.py
│       ├── chunking.py
│       ├── embeddings.py
│       └── vector_store.py
├── database/
│   └── init.sql             # Database schema
├── docker-compose.yml
├── requirements.txt
└── .env
```

## Configuration

Key environment variables in `.env`:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Your OpenAI API key
- `CHUNK_SIZE`: Token count per chunk (default: 512)
- `CHUNK_OVERLAP`: Overlapping tokens (default: 50)
- `DEFAULT_TOP_K`: Default search results (default: 5)

## How It Works

1. **Upload File**: Files are uploaded to a corpus
2. **Text Extraction**: Text is extracted based on file type
3. **Chunking**: Text is split into 512-token chunks with 50-token overlap
4. **Embedding**: Each chunk is embedded using OpenAI ada-002
5. **Storage**: Chunks and embeddings are stored in PostgreSQL
6. **Search**: Query is embedded and compared using cosine similarity
7. **Results**: Top-k most similar chunks are returned

## Database Schema

- **corpus**: Document collections
- **files**: Uploaded files metadata
- **document_chunks**: Text chunks with vector embeddings

Cascade delete ensures removing a corpus or file automatically deletes all associated data.

## Development

Run with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## License

MIT
