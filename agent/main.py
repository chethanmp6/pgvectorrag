"""CLI interface for RAG search agent"""

import asyncio
import sys
import logging
from typing import Optional

from agent.agent import RAGAgent
from agent.tools import SearchTool
from agent.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGAgentCLI:
    """Command-line interface for RAG search agent"""
    
    def __init__(self):
        """Initialize CLI"""
        # Validate corpus_id is set
        if not config.corpus_id:
            print("❌ Error: CORPUS_ID not set in .env")
            print("   Please add: CORPUS_ID=your-corpus-uuid-here")
            sys.exit(1)
        
        # Initialize search tool with direct database access
        self.search_tool = SearchTool(
            database_url=config.database_url,
            corpus_id=config.corpus_id
        )
        self.agent = RAGAgent(self.search_tool, config)
    
    async def run(self):
        """Main CLI loop"""
        try:
            self._print_header()
            
            # Show help
            self._show_help()
            
            # Chat loop
            while True:
                try:
                    user_input = input("\n💬 You > ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.startswith("/"):
                        should_continue = await self._handle_command(user_input)
                        if not should_continue:
                            break
                        continue
                    
                    # Process message (no corpus_id needed)
                    print("\n🤔 Thinking...")
                    response = await self.agent.process_message(user_input)
                    
                    print(f"\n🤖 Agent >\n{response}")
                    
                except KeyboardInterrupt:
                    print("\n\nUse /exit to quit")
                    continue
                except EOFError:
                    break
                except Exception as e:
                    logger.error(f"Error in chat loop: {e}")
                    print(f"\n❌ Error: {str(e)}")
        
        finally:
            await self.search_tool.close()
            print("\n👋 Goodbye!")
    
    def _print_header(self):
        """Print welcome header"""
        print("=" * 70)
        print("🤖 RAG Search Agent (Direct Database)".center(70))
        print("=" * 70)
        print("\nAI-powered conversational search for your documents")
        print(f"Using LiteLLM Proxy: {config.litellm_base_url}")
        print(f"Corpus ID: {config.corpus_id}")
        print(f"Database: {config.database_url.split('@')[1] if '@' in config.database_url else 'localhost'}")
        print()
    
    
    async def _handle_command(self, command: str) -> bool:
        """
        Handle special commands
        
        Returns:
            True to continue, False to exit
        """
        cmd = command.lower().strip()
        
        if cmd == "/help":
            self._show_help()
        
        elif cmd == "/history":
            self._show_history()
        
        elif cmd == "/clear":
            self.agent.clear_history()
            print("✅ Conversation history cleared")
        
        elif cmd == "/info":
            self._show_info()
        
        elif cmd == "/exit" or cmd == "/quit":
            return False
        
        else:
            print(f"❌ Unknown command: {command}")
            print("   Type /help for available commands")
        
        return True
    
    def _show_help(self):
        """Show help message"""
        print("\n" + "=" * 70)
        print("📖 Available Commands".center(70))
        print("=" * 70)
        print("  /help     - Show this help message")
        print("  /history  - Show conversation history")
        print("  /clear    - Clear conversation history")
        print("  /info     - Show agent information")
        print("  /exit     - Exit the agent")
        print("\n💡 Tip: Just type your question to search the documents!")
        print("=" * 70)
    
    def _show_history(self):
        """Show conversation history"""
        history = self.agent.get_conversation_history()
        
        if not history:
            print("\n📝 No conversation history yet")
            return
        
        print("\n" + "=" * 70)
        print("📝 Conversation History".center(70))
        print("=" * 70)
        
        for i, (user_msg, agent_msg) in enumerate(history, 1):
            print(f"\n[{i}] You: {user_msg}")
            print(f"    Agent: {agent_msg[:100]}...")
        
        print("=" * 70)
    
    
    def _show_info(self):
        """Show agent information"""
        print("\n" + "=" * 70)
        print("� Agent Information".center(70))
        print("=" * 70)
        print(f"Model: {config.litellm_chat_model}")
        print(f"Temperature: {config.temperature}")
        print(f"Top-K Results: {config.default_top_k}")
        print(f"Corpus ID: {config.corpus_id}")
        print(f"Conversation History: {len(self.agent.get_conversation_history())} exchanges")
        print("=" * 70)


async def main():
    """Main entry point"""
    cli = RAGAgentCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
