"""
Test script to verify LiteLLM proxy integration for embeddings
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.embeddings import EmbeddingService
from app.config import settings


async def test_litellm_embedding():
    """Test LiteLLM proxy embedding generation"""
    
    print("=" * 60)
    print("LiteLLM Proxy Embedding Test")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Base URL: {settings.litellm_base_url}")
    print(f"  Model: {settings.litellm_embedding_model}")
    print(f"  API Key: {settings.litellm_api_key[:10]}...")
    print()
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    
    # Test 1: Single embedding
    print("Test 1: Single text embedding")
    print("-" * 60)
    test_text = "The quick brown fox jumps over the lazy dog"
    print(f"Input: {test_text}")
    
    try:
        embedding = await embedding_service.generate_embedding(test_text)
        print(f"✓ Success! Generated embedding with {len(embedding)} dimensions")
        print(f"  First 5 values: {embedding[:5]}")
        print()
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print()
        return False
    
    # Test 2: Batch embeddings
    print("Test 2: Batch embeddings")
    print("-" * 60)
    test_texts = [
        "Machine learning is a subset of artificial intelligence",
        "Natural language processing enables computers to understand text",
        "Deep learning uses neural networks with multiple layers"
    ]
    print(f"Input: {len(test_texts)} texts")
    
    try:
        embeddings = await embedding_service.generate_embeddings_batch(test_texts)
        print(f"✓ Success! Generated {len(embeddings)} embeddings")
        for i, emb in enumerate(embeddings):
            print(f"  Embedding {i+1}: {len(emb)} dimensions")
        print()
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print()
        return False
    
    # Test 3: Query embedding
    print("Test 3: Query embedding")
    print("-" * 60)
    query = "What is artificial intelligence?"
    print(f"Query: {query}")
    
    try:
        query_embedding = await embedding_service.generate_query_embedding(query)
        print(f"✓ Success! Generated query embedding with {len(query_embedding)} dimensions")
        print()
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print()
        return False
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    print("\nStarting LiteLLM proxy embedding tests...\n")
    print("NOTE: Make sure LiteLLM proxy is running at http://localhost:4000\n")
    
    success = asyncio.run(test_litellm_embedding())
    
    if success:
        print("\n✓ LiteLLM integration is working correctly!")
        sys.exit(0)
    else:
        print("\n✗ LiteLLM integration test failed. Please check:")
        print("  1. LiteLLM proxy is running at http://localhost:4000")
        print("  2. API key is correct: sk-3cPU913F4530vHZvmpxOWA")
        print("  3. Model 'text-embedding-ada-002' is available")
        sys.exit(1)
