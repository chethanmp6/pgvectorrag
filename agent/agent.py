"""Core RAG search agent with LiteLLM integration"""

from openai import AsyncOpenAI
from typing import List, Dict, Tuple
import logging

from agent.tools import SearchTool
from agent.config import AgentConfig

logger = logging.getLogger(__name__)


class RAGAgent:
    """AI agent for conversational RAG search"""
    
    def __init__(self, search_tool: SearchTool, config: AgentConfig):
        """
        Initialize RAG agent
        
        Args:
            search_tool: Search tool for direct database access
            config: Agent configuration
        """
        self.search_tool = search_tool
        self.config = config
        
        # Initialize LiteLLM client (OpenAI-compatible)
        self.llm = AsyncOpenAI(
            base_url=config.litellm_base_url,
            api_key=config.litellm_api_key
        )
        
        self.model = config.litellm_chat_model
        self.temperature = config.temperature
        self.conversation_history: List[Tuple[str, str]] = []
    
    async def process_message(
        self, 
        user_message: str
    ) -> str:
        """
        Process user message and return response
        
        Args:
            user_message: User's question or message
            
        Returns:
            Agent's response with answer and sources
        """
        try:
            # 1. Extract search query using LiteLLM
            logger.info(f"Processing message: {user_message}")
            search_query = await self._extract_query(user_message)
            logger.info(f"Extracted query: {search_query}")
            
            # 2. Search using direct database access
            results = await self.search_tool.search(
                search_query, 
                top_k=self.config.default_top_k
            )
            logger.info(f"Found {len(results)} results")
            
            # 3. Format response using LiteLLM
            response = await self._format_response(user_message, results)
            
            # 4. Update conversation history
            self._update_history(user_message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def _extract_query(self, user_message: str) -> str:
        """
        Use LiteLLM to extract search query from user message
        
        Args:
            user_message: User's natural language message
            
        Returns:
            Extracted search query
        """
        try:
            response = await self.llm.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Extract the core search query from the user's message. 
                        Return only the search query terms, nothing else. 
                        Keep it concise and focused on the main topic."""
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                temperature=0.3,
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error extracting query: {e}")
            # Fallback to original message
            return user_message
    
    async def _format_response(
        self, 
        user_query: str, 
        search_results: List[Dict]
    ) -> str:
        """
        Use LiteLLM to synthesize answer from search results
        
        Args:
            user_query: Original user question
            search_results: List of search results from SearchTool
            
        Returns:
            Formatted response with answer and sources
        """
        # Format search results for LLM context
        context = self._format_results_for_llm(search_results)
        
        # Build conversation context
        history_context = self._build_history_context()
        
        try:
            response = await self.llm.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful assistant that answers questions based on 
                        provided document chunks. Synthesize a clear, concise answer using the 
                        search results. Always cite your sources at the end.
                        
                        Format your response as:
                        [Your synthesized answer based on the documents]
                        
                        Sources:
                        - [filename] (similarity: X.XX)
                        - [filename] (similarity: X.XX)
                        
                        If the search results don't contain relevant information, say so politely."""
                    },
                    *history_context,
                    {
                        "role": "user",
                        "content": f"""Question: {user_query}
                        
Search Results:
{context}

Please answer the question based on these search results."""
                    }
                ],
                temperature=self.temperature,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            # Fallback to simple formatting
            return self._simple_format_results(search_results)
    
    def _format_results_for_llm(self, search_results: List[Dict]) -> str:
        """Format search results as context for LLM"""
        if not search_results:
            return "No relevant documents found."
        
        formatted = []
        for i, result in enumerate(search_results, 1):
            formatted.append(
                f"[Document {i}]\n"
                f"File: {result['filename']}\n"
                f"Similarity: {result['similarity_score']:.2f}\n"
                f"Content: {result['chunk_text']}\n"
            )
        
        return "\n".join(formatted)
    
    def _simple_format_results(self, search_results: List[Dict]) -> str:
        """Simple fallback formatting without LLM"""
        if not search_results:
            return "I couldn't find any relevant information in the documents."
        
        response = "Here's what I found:\n\n"
        for result in search_results[:3]:
            response += f"📄 {result['filename']}\n"
            response += f"   {result['chunk_text'][:200]}...\n"
            response += f"   (similarity: {result['similarity_score']:.2f})\n\n"
        
        return response
    
    def _build_history_context(self) -> List[Dict]:
        """Build conversation history for LLM context"""
        history = []
        # Include last few exchanges for context
        for user_msg, agent_msg in self.conversation_history[-3:]:
            history.append({"role": "user", "content": user_msg})
            history.append({"role": "assistant", "content": agent_msg})
        return history
    
    def _update_history(self, user_message: str, response: str):
        """Update conversation history"""
        self.conversation_history.append((user_message, response))
        
        # Keep only recent history
        if len(self.conversation_history) > self.config.max_conversation_history:
            self.conversation_history = self.conversation_history[-self.config.max_conversation_history:]
    
    def get_conversation_history(self) -> List[Tuple[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
