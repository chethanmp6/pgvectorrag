# RAG Search Tool

A simple tool for searching the RAG corpus directly from the agent without HTTP overhead.

## Overview

The `SearchTool` provides direct database access to search a configured corpus. It's designed to be used by AI agents as a function/tool that can be called to retrieve relevant documents.

## Features

- ✅ Direct database access (no HTTP calls)
- ✅ Corpus ID from environment configuration
- ✅ Connection pooling for performance
- ✅ Simple async interface
- ✅ Returns structured search results

## Configuration

Add to your `.env` file:

```bash
# Database connection
DATABASE_URL=postgresql+asyncpg://litellm_user:password@localhost:5432/ragdb

# Corpus to search
CORPUS_ID=your-corpus-uuid-here

# Search settings (optional)
DEFAULT_TOP_K=5
```

## Usage

### Basic Usage

```python
from agent.tools import SearchTool
from agent.config import config

# Initialize tool
search_tool = SearchTool(
    database_url=config.database_url,
    corpus_id=config.corpus_id
)

# Search
results = await search_tool.search(
    query="What is machine learning?",
    top_k=5
)

# Results format
for result in results:
    print(f"File: {result['filename']}")
    print(f"Similarity: {result['similarity_score']}")
    print(f"Text: {result['chunk_text']}")
```

### With LLM Agent

The search tool can be integrated with an LLM agent as a callable function:

```python
from openai import AsyncOpenAI
from agent.tools import SearchTool
from agent.config import config

# Initialize
llm = AsyncOpenAI(base_url=config.litellm_base_url, api_key=config.litellm_api_key)
search_tool = SearchTool(config.database_url, config.corpus_id)

# Define tool for LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search the knowledge base for relevant documents",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Agent loop
response = await llm.chat.completions.create(
    model=config.litellm_chat_model,
    messages=[{"role": "user", "content": "What is neural network?"}],
    tools=tools
)

# If LLM wants to call the tool
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    if tool_call.function.name == "search_documents":
        args = json.loads(tool_call.function.arguments)
        results = await search_tool.search(args["query"], args.get("top_k", 5))
        # Send results back to LLM...
```

## API Reference

### SearchTool

#### `__init__(database_url: str, corpus_id: str)`

Initialize the search tool.

**Parameters:**
- `database_url`: PostgreSQL connection string (asyncpg format)
- `corpus_id`: UUID of the corpus to search

#### `async search(query: str, top_k: int = 5) -> List[Dict]`

Search the corpus for relevant documents.

**Parameters:**
- `query`: Search query text
- `top_k`: Number of results to return (default: 5)

**Returns:**
List of dictionaries with:
- `chunk_text`: The document chunk text
- `similarity_score`: Cosine similarity score (0-1)
- `filename`: Source filename
- `file_id`: File UUID
- `chunk_index`: Index of the chunk in the file
- `metadata`: Additional metadata (if any)

#### `async close()`

Close database connections. Call this when done using the tool.

## Example

See [`agent/examples/search_tool_example.py`](file:///Users/apple/Documents/Virtusa/virtusavertexrag/agent/examples/search_tool_example.py) for a complete example.

```bash
# Run the example
python -m agent.examples.search_tool_example
```

## Performance

- **Direct database access**: ~50-100ms faster than HTTP API calls
- **Connection pooling**: Reuses database connections for efficiency
- **Async operations**: Non-blocking I/O for better concurrency

## Error Handling

```python
try:
    results = await search_tool.search("query")
except Exception as e:
    print(f"Search error: {e}")
    # Handle error (corpus not found, database connection issue, etc.)
```

## Notes

- The corpus ID must be set in `.env` before using the tool
- Ensure the PostgreSQL database is accessible
- The tool uses the same vector search logic as the RAG API endpoint
- Connection pool size: 5 connections, max overflow: 10

## Integration with Existing Agent

To integrate with the existing conversational agent in `agent/main.py`, you can replace the HTTP-based `RAGClient` with the `SearchTool` for better performance.
