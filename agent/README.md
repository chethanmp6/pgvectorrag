# RAG Search Agent

AI-powered conversational search agent with direct database access for fast semantic search.

## Features

- 🤖 **Conversational Interface**: Natural language interaction
- 🔍 **Semantic Search**: Direct database access for fast vector search
- 🧠 **LiteLLM Integration**: Uses LiteLLM proxy for query understanding and response synthesis
- 📝 **Conversation History**: Maintains context across questions
- 📊 **Source Citation**: Shows document sources with similarity scores
- ⚡ **High Performance**: Direct database queries (~50-100ms faster than HTTP)

## Architecture

```
User Input → Agent → LiteLLM (Query Extraction)
                ↓
                → SearchTool → Database (Direct Vector Search)
                ↓
                → LiteLLM (Response Synthesis)
                ↓
           Formatted Answer + Sources
```

**Direct Database Access**: No HTTP overhead, faster queries, simpler architecture.

## Prerequisites

1. **PostgreSQL Database** with pgvector extension
2. **LiteLLM Proxy** running at `http://localhost:4000`
3. **Corpus created** with documents uploaded
4. **Corpus ID** from your database

## Installation

Dependencies are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Get Your Corpus ID

Find your corpus ID from the database or RAG API:

```bash
# Using psql
psql -h localhost -U litellm_user -d ragdb -c "SELECT id, name FROM corpus;"

# Or via RAG API
curl http://localhost:8000/corpus
```

### 2. Set Environment Variables

Add to `.env`:

```bash
# Database Connection (REQUIRED)
DATABASE_URL=postgresql+asyncpg://litellm_user:password@localhost:5432/ragdb

# Corpus to Search (REQUIRED)
CORPUS_ID=your-corpus-uuid-here

# LiteLLM Proxy (REQUIRED)
LITELLM_BASE_URL=http://localhost:4000/v1
LITELLM_API_KEY=sk-your-api-key
LITELLM_CHAT_MODEL=gemini-2.5-flash
LITELLM_EMBEDDING_MODEL=text-embedding-ada-002

# Agent Behavior (OPTIONAL)
DEFAULT_TOP_K=5
AGENT_TEMPERATURE=0.7
MAX_CONVERSATION_HISTORY=10
```

## Usage

### Start the Agent

```bash
python -m agent.main
```

### Example Session

```
======================================================================
          🤖 RAG Search Agent (Direct Database)              
======================================================================

AI-powered conversational search for your documents
Using LiteLLM Proxy: http://localhost:4000/v1
Corpus ID: c878f297-fca8-4d50-90e5-acaa74716e25
Database: localhost:5432/ragdb

======================================================================
                    📖 Available Commands                        
======================================================================
  /help     - Show this help message
  /history  - Show conversation history
  /clear    - Clear conversation history
  /info     - Show agent information
  /exit     - Exit the agent

💡 Tip: Just type your question to search the documents!
======================================================================

💬 You > What is a neural network?

🤔 Thinking...

🤖 Agent >
A neural network is a computational model inspired by biological neural 
networks in the brain. It consists of interconnected nodes (neurons) 
organized in layers that process information through weighted connections. 
The network learns by adjusting these weights based on training data.

Sources:
- neural_networks.pdf (similarity: 0.92)
- ml_basics.pdf (similarity: 0.87)

💬 You > How do they learn?

🤔 Thinking...

🤖 Agent >
Neural networks learn through a process called backpropagation. During 
training, the network makes predictions, compares them to actual values, 
calculates the error, and adjusts weights backwards through the layers 
to minimize this error over time.

Sources:
- neural_networks.pdf (similarity: 0.89)
- deep_learning.pdf (similarity: 0.84)
```

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/history` | View conversation history |
| `/clear` | Clear conversation history |
| `/info` | Show agent configuration and stats |
| `/exit` | Exit the agent |

## How It Works

1. **User Input**: You ask a question in natural language
2. **Query Extraction**: LiteLLM extracts the core search query from your message
3. **Vector Search**: SearchTool performs direct database similarity search
4. **Response Synthesis**: LiteLLM generates a natural answer using search results
5. **Display**: Formatted response with source citations shown to user

## Performance

| Metric | Value |
|--------|-------|
| Query Latency | ~80-120ms |
| Database Access | Direct (no HTTP) |
| Connection Pool | 5 connections |
| Max Overflow | 10 connections |

**~50-100ms faster** than HTTP-based approach.

## Troubleshooting

### "CORPUS_ID not set in .env"

**Solution:**
1. Find your corpus ID: `curl http://localhost:8000/corpus`
2. Add to `.env`: `CORPUS_ID=your-uuid-here`

### "Error connecting to database"

**Causes:**
- Database not running
- Wrong credentials in `DATABASE_URL`
- Network issues

**Solutions:**
```bash
# Check database is running
docker ps | grep postgres

# Test connection
psql -h localhost -U litellm_user -d ragdb

# Verify DATABASE_URL in .env
```

### "Invalid model name"

**Solution:**
- Check available models: `curl http://localhost:4000/v1/models`
- Update `LITELLM_CHAT_MODEL` in `.env` to a valid model

### "Error formatting response"

**Causes:**
- LiteLLM proxy not running
- Invalid API key
- Model not available

**Solutions:**
```bash
# Check LiteLLM is running
curl http://localhost:4000/health

# Verify LITELLM_API_KEY in .env
```

## Development

### File Structure

```
agent/
├── __init__.py          # Package init
├── config.py            # Configuration settings
├── agent.py             # Core agent logic
├── main.py              # CLI interface
├── tools/
│   ├── __init__.py      # Tools package
│   ├── search_tool.py   # Direct database search
│   └── README.md        # Tool documentation
└── examples/
    └── search_tool_example.py
```

### Key Components

#### SearchTool (`agent/tools/search_tool.py`)
- Direct database access
- Vector similarity search
- Connection pooling
- Async operations

#### RAGAgent (`agent/agent.py`)
- Query extraction via LLM
- Response synthesis
- Conversation history management
- Source citation

#### CLI (`agent/main.py`)
- User interface
- Command handling
- Session management

### Adding Features

**New Commands:**
Add to `_handle_command()` in `main.py`:
```python
elif cmd == "/mycommand":
    self._my_custom_handler()
```

**Custom Prompts:**
Modify system prompts in `agent.py`:
```python
"content": """Your custom system prompt here..."""
```

**Different Models:**
Change in `.env`:
```bash
LITELLM_CHAT_MODEL=gpt-4
```

## Advanced Usage

### Using SearchTool Directly

```python
from agent.tools import SearchTool
from agent.config import config

# Initialize
search_tool = SearchTool(
    database_url=config.database_url,
    corpus_id=config.corpus_id
)

# Search
results = await search_tool.search(
    query="machine learning",
    top_k=5
)

# Results format
for result in results:
    print(f"File: {result['filename']}")
    print(f"Score: {result['similarity_score']}")
    print(f"Text: {result['chunk_text']}")

# Cleanup
await search_tool.close()
```

### Integration with Custom Agents

See [`agent/tools/README.md`](tools/README.md) for detailed integration guide.

## Comparison: Direct vs HTTP

| Feature | Direct Database | HTTP API |
|---------|----------------|----------|
| Speed | ⚡ Fast (~80-120ms) | 🐌 Slower (~150-200ms) |
| Dependencies | Database only | Database + API |
| Setup | Simpler | More complex |
| Corpus Selection | Config-based | Runtime selection |
| Use Case | Production agents | Interactive testing |

## Migration from HTTP Version

If upgrading from the old HTTP-based agent:

**Old (HTTP):**
```python
from agent.rag_client import RAGClient

rag_client = RAGClient("http://localhost:8000")
response = await agent.process_message(msg, corpus_id)
```

**New (Direct):**
```python
from agent.tools import SearchTool

search_tool = SearchTool(db_url, corpus_id)
response = await agent.process_message(msg)  # No corpus_id needed
```

## License

MIT
