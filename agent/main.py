"""CLI interface for RAG search agent"""

import asyncio
import sys
import logging
from typing import Optional

from agent.agent import RAGAgent
from agent.rag_client import RAGClient
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
        self.rag_client = RAGClient(config.rag_api_base_url)
        self.agent = RAGAgent(self.rag_client, config)
        self.current_corpus_id: Optional[str] = None
        self.current_corpus_name: Optional[str] = None
    
    async def run(self):
        """Main CLI loop"""
        try:
            self._print_header()
            
            # Select corpus
            await self._select_corpus()
            
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
                        await self._handle_command(user_input)
                        continue
                    
                    # Process message
                    print("\n🤔 Thinking...")
                    response = await self.agent.process_message(
                        user_input, 
                        self.current_corpus_id
                    )
                    
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
            await self.rag_client.close()
            print("\n👋 Goodbye!")
    
    def _print_header(self):
        """Print welcome header"""
        print("=" * 70)
        print("🤖 RAG Search Agent".center(70))
        print("=" * 70)
        print("\nAI-powered conversational search for your documents")
        print(f"Using LiteLLM Proxy: {config.litellm_base_url}")
        print(f"RAG API: {config.rag_api_base_url}")
        print()
    
    async def _select_corpus(self):
        """Let user select corpus"""
        try:
            corpus_list = await self.rag_client.list_corpus()
            
            if not corpus_list:
                print("❌ No corpus found. Please create one first via Swagger UI.")
                print(f"   Visit: {config.rag_api_base_url}/docs")
                sys.exit(1)
            
            print("📚 Available Corpus:")
            print("-" * 70)
            for i, corpus in enumerate(corpus_list, 1):
                file_count = corpus.get('file_count', 0)
                print(f"  [{i}] {corpus['name']}")
                print(f"      {corpus.get('description', 'No description')}")
                print(f"      Files: {file_count}")
                print()
            
            while True:
                try:
                    choice_input = input("Select corpus number: ").strip()
                    choice = int(choice_input) - 1
                    
                    if 0 <= choice < len(corpus_list):
                        selected = corpus_list[choice]
                        self.current_corpus_id = selected['id']
                        self.current_corpus_name = selected['name']
                        print(f"\n✅ Using corpus: {self.current_corpus_name}")
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(corpus_list)}")
                except ValueError:
                    print("Please enter a valid number")
                except KeyboardInterrupt:
                    print("\n\nExiting...")
                    sys.exit(0)
        
        except Exception as e:
            logger.error(f"Error selecting corpus: {e}")
            print(f"❌ Error connecting to RAG API: {str(e)}")
            print(f"   Make sure the RAG API is running at {config.rag_api_base_url}")
            sys.exit(1)
    
    async def _handle_command(self, command: str):
        """Handle special commands"""
        cmd = command.lower().strip()
        
        if cmd == "/help":
            self._show_help()
        
        elif cmd == "/corpus":
            await self._select_corpus()
        
        elif cmd == "/history":
            self._show_history()
        
        elif cmd == "/clear":
            self.agent.clear_history()
            print("✅ Conversation history cleared")
        
        elif cmd == "/info":
            await self._show_corpus_info()
        
        elif cmd == "/exit" or cmd == "/quit":
            print("\n👋 Goodbye!")
            await self.rag_client.close()
            sys.exit(0)
        
        else:
            print(f"❌ Unknown command: {command}")
            print("   Type /help for available commands")
    
    def _show_help(self):
        """Show help message"""
        print("\n" + "=" * 70)
        print("📖 Available Commands".center(70))
        print("=" * 70)
        print("  /help     - Show this help message")
        print("  /corpus   - Switch to a different corpus")
        print("  /history  - Show conversation history")
        print("  /clear    - Clear conversation history")
        print("  /info     - Show current corpus information")
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
    
    async def _show_corpus_info(self):
        """Show current corpus information"""
        try:
            corpus_info = await self.rag_client.get_corpus(self.current_corpus_id)
            
            print("\n" + "=" * 70)
            print("📚 Corpus Information".center(70))
            print("=" * 70)
            print(f"Name: {corpus_info['name']}")
            print(f"Description: {corpus_info.get('description', 'No description')}")
            print(f"Files: {corpus_info.get('file_count', 0)}")
            print(f"Created: {corpus_info.get('created_at', 'Unknown')}")
            
            if corpus_info.get('files'):
                print("\n📄 Files in corpus:")
                for file in corpus_info['files']:
                    chunks = file.get('chunk_count', 0)
                    print(f"  - {file['filename']} ({chunks} chunks)")
            
            print("=" * 70)
        
        except Exception as e:
            logger.error(f"Error getting corpus info: {e}")
            print(f"❌ Error: {str(e)}")


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
