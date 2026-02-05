# RAG System with PostgreSQL pgvector

A production-ready Retrieval-Augmented Generation (RAG) system built with FastAPI and PostgreSQL pgvector, similar to Google Vertex AI RAG Engine.

## Features

- 🗂️ **Corpus Management**: Create, list, retrieve, and delete document collections
- 📄 **Multi-Format Support**: PDF, DOCX, TXT, and Markdown files
- 🔍 **Semantic Search**: Vector similarity search using LiteLLM proxy for embeddings
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
│  │  - Embedding (LiteLLM)    │  │
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

## Agent Architecture

The system includes an AI-powered conversational search agent with direct database access:

```
User → Agent CLI → SearchTool → PostgreSQL (Direct)
           ↓
      LiteLLM Proxy (Query Understanding & Response Synthesis)
```

**Agent Features:**
- 🤖 Natural language queries
- ⚡ Direct database access (~50-100ms faster than HTTP)
- 🧠 LiteLLM-powered query extraction and response synthesis
- 📝 Conversation history
- 📊 Source citations

See [`agent/README.md`](agent/README.md) for agent documentation.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- LiteLLM proxy running (with embeddings model configured)

### Setup

1. **Clone and navigate to the project**:
   ```bash
   cd /Users/apple/Documents/Virtusa/virtusavertexrag
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and configure LiteLLM proxy settings**:
   ```
   LITELLM_BASE_URL=http://localhost:4000/v1
   LITELLM_API_KEY=your-litellm-api-key-here
   LITELLM_EMBEDDING_MODEL=text-embedding-ada-002
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
│       ├── vector_store.py
│       └── search_service.py
├── agent/
│   ├── main.py              # Agent CLI
│   ├── agent.py             # Core agent logic
│   ├── config.py            # Agent configuration
│   ├── tools/
│   │   ├── search_tool.py   # Direct database search
│   │   └── README.md        # Tool documentation
│   └── examples/
│       └── search_tool_example.py
├── database/
│   └── init.sql             # Database schema
├── docker-compose.yml
├── requirements.txt
└── .env
```

## Configuration

All configuration must be set in `.env` file (no hardcoded defaults):

### Required Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ragdb

# LiteLLM Proxy
LITELLM_BASE_URL=http://localhost:4000/v1
LITELLM_API_KEY=your-litellm-api-key-here
LITELLM_EMBEDDING_MODEL=text-embedding-ada-002
```

### Optional Variables

```bash
# Application
APP_HOST=0.0.0.0
APP_PORT=8000

# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Search
DEFAULT_TOP_K=5
```

### Agent-Specific Variables

For the conversational agent, also add:

```bash
# Agent Configuration
CORPUS_ID=your-corpus-uuid-here
LITELLM_CHAT_MODEL=gemini-2.5-flash
AGENT_TEMPERATURE=0.7
MAX_CONVERSATION_HISTORY=10
```

## How It Works

1. **Upload File**: Files are uploaded to a corpus
2. **Text Extraction**: Text is extracted based on file type
3. **Chunking**: Text is split into 512-token chunks with 50-token overlap
4. **Embedding**: Each chunk is embedded using LiteLLM proxy (OpenAI-compatible)
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
