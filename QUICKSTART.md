# Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ installed
- OpenAI API key

## Setup Steps

### 1. Option A: Run everything with Docker Compose (Recommended)
```bash
docker-compose up -d --build
```
This starts both PostgreSQL and the FastAPI application.

### 1. Option B: Manual Local Setup
#### Start PostgreSQL only
```bash
docker-compose up -d postgres
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Edit `.env` file and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Verify Setup
```bash
python test_setup.py
```

You should see:
```
✅ PostgreSQL connected
✅ pgvector extension installed
✅ Tables found: corpus, document_chunks, files
🎉 All checks passed!
```

### 6. Run the Application
```bash
python -m app.main
```

The API will be available at: `http://localhost:8000`

### 7. Explore API Documentation
Visit: `http://localhost:8000/docs`

## Quick Test

### Create a Corpus
```bash
curl -X POST http://localhost:8000/corpus \
  -H "Content-Type: application/json" \
  -d '{"name": "test_corpus", "description": "My first corpus"}'
```

Save the `id` from the response.

### Upload a File
```bash
curl -X POST http://localhost:8000/corpus/{corpus_id}/files \
  -F "file=@your-document.pdf"
```

### Search
```bash
curl -X POST http://localhost:8000/corpus/{corpus_id}/query \
  -H "Content-Type: application/json" \
  -d '{"query": "your search query", "top_k": 5}'
```

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs postgres
```

### Port Already in Use
If port 5432 is already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Change to different port
```

Then update `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql+asyncpg://raguser:ragpassword@localhost:5433/ragdb
```

## Stopping the Application

```bash
# Stop FastAPI (Ctrl+C in terminal)

# Stop PostgreSQL
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Next Steps

- Check out the full [README.md](README.md) for detailed documentation
- Explore the API at `http://localhost:8000/docs`
- Review the [walkthrough.md](walkthrough.md) for implementation details
