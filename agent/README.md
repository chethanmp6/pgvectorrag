# RAG Search Agent

AI-powered conversational search agent for testing RAG functionality.

## Features

- 🤖 **Conversational Interface**: Natural language interaction
- 🔍 **Semantic Search**: Powered by RAG system's vector search
- 🧠 **LiteLLM Integration**: Uses LiteLLM proxy for query understanding and response synthesis
- 📝 **Conversation History**: Maintains context across questions
- 📊 **Source Citation**: Shows document sources with similarity scores

## Architecture

```
User Input → Agent → LiteLLM Proxy (Query Extraction)
                ↓
                → RAG API (Semantic Search)
                ↓
                → LiteLLM Proxy (Response Synthesis)
                ↓
           Formatted Answer + Sources
```

## Prerequisites

1. **RAG API running** at `http://localhost:8000`
2. **LiteLLM Proxy running** at `http://localhost:4000`
3. **Corpus created** with documents uploaded (via Swagger UI)

## Installation

Dependencies are already in `requirements.txt`. If needed:

```bash
pip install httpx>=0.27.0
```

## Usage

### Start the Agent

```bash
python -m agent.main
```

### Example Session

```
======================================================================
                        🤖 RAG Search Agent
======================================================================

AI-powered conversational search for your documents
Using LiteLLM Proxy: http://localhost:4000/v1
RAG API: http://localhost:8000

📚 Available Corpus:
----------------------------------------------------------------------
  [1] ML Documentation
      Machine learning documentation and papers
      Files: 3

Select corpus number: 1

✅ Using corpus: ML Documentation

======================================================================
                        📖 Available Commands
======================================================================
  /help     - Show this help message
  /corpus   - Switch to a different corpus
  /history  - Show conversation history
  /clear    - Clear conversation history
  /info     - Show current corpus information
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
| `/corpus` | Switch to a different corpus |
| `/history` | View conversation history |
| `/clear` | Clear conversation history |
| `/info` | Show current corpus details |
| `/exit` | Exit the agent |

## Configuration

The agent uses settings from `.env`:

```bash
# LiteLLM Proxy (for both embeddings and chat)
LITELLM_BASE_URL=http://localhost:4000/v1
LITELLM_API_KEY=sk-3cPU913F4530vHZvmpxOWA
LITELLM_CHAT_MODEL=gpt-3.5-turbo
LITELLM_EMBEDDING_MODEL=text-embedding-ada-002

# RAG API
RAG_API_BASE_URL=http://localhost:8000
DEFAULT_TOP_K=5

# Agent Behavior
AGENT_TEMPERATURE=0.7
```

## How It Works

1. **User Input**: You ask a question in natural language
2. **Query Extraction**: LiteLLM extracts the core search query
3. **Semantic Search**: RAG API finds relevant document chunks
4. **Response Synthesis**: LiteLLM generates a natural answer with sources
5. **Display**: Formatted response shown to user

## Troubleshooting

### "No corpus found"
- Create a corpus via Swagger UI: `http://localhost:8000/docs`
- Upload documents to the corpus

### "Error connecting to RAG API"
- Ensure RAG API is running: `python -m app.main`
- Check the URL in `.env`

### "Error connecting to LiteLLM"
- Ensure LiteLLM proxy is running
- Verify the API key is correct

## Development

### File Structure

```
agent/
├── __init__.py          # Package init
├── config.py            # Configuration
├── rag_client.py        # RAG API client
├── agent.py             # Core agent logic
└── main.py              # CLI interface
```

### Adding Features

- **New commands**: Add to `_handle_command()` in `main.py`
- **Custom prompts**: Modify system prompts in `agent.py`
- **Different models**: Change `LITELLM_CHAT_MODEL` in `.env`

## License

MIT
