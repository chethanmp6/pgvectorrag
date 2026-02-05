"""
Example: Using the Search Tool

This example shows how to use the search tool to query the RAG corpus.
"""

import asyncio
from agent.tools import SearchTool
from agent.config import config


async def main():
    """Example usage of search tool"""
    
    # Initialize search tool with config
    search_tool = SearchTool(
        database_url=config.database_url,
        corpus_id=config.corpus_id
    )
    
    try:
        # Search for documents
        query = "What is machine learning?"
        results = await search_tool.search(query, top_k=3)
        
        print(f"Query: {query}\n")
        print(f"Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  File: {result['filename']}")
            print(f"  Similarity: {result['similarity_score']:.4f}")
            print(f"  Text: {result['chunk_text'][:200]}...")
            print()
    
    finally:
        await search_tool.close()


if __name__ == "__main__":
    asyncio.run(main())
