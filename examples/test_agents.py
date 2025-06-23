"""
Test script for the Events Articles Chatbot agents.

This script demonstrates how to use the SQL agent, RAG agent, and supervisor
to query events and articles data.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents import EventsArticlesChatbot
from sql_agent.agent import SQLAgent
from rag_agent.agent import RAGAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_sql_agent():
    """Test the SQL agent with various queries."""
    print("\n" + "="*60)
    print("TESTING SQL AGENT")
    print("="*60)
    
    try:
        sql_agent = SQLAgent()
        
        test_queries = [
            "Show me all events",
            "How many articles are in the database?",
            "Find events happening in 2024",
            "List the most recent articles",
            "Show me events with their locations"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            print("-" * 40)
            
            result = sql_agent.query(query)
            
            if result["success"]:
                print(f"Response: {result['response'][:500]}...")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            print()
    
    except Exception as e:
        print(f"Error testing SQL agent: {e}")


def test_rag_agent():
    """Test the RAG agent with various queries."""
    print("\n" + "="*60)
    print("TESTING RAG AGENT")
    print("="*60)
    
    try:
        rag_agent = RAGAgent()
        
        test_queries = [
            "Tell me about artificial intelligence",
            "What articles discuss technology trends?",
            "Explain machine learning concepts",
            "Find content about business strategies",
            "What information is available about events?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            print("-" * 40)
            
            result = rag_agent.query(query)
            
            if result["success"]:
                print(f"Response: {result['response'][:500]}...")
                
                # Show retrieved documents
                retrieved_docs = result.get("retrieved_docs", [])
                if retrieved_docs:
                    print(f"\nRetrieved {len(retrieved_docs)} documents:")
                    for i, doc in enumerate(retrieved_docs[:3]):  # Show first 3
                        print(f"  {i+1}. {doc.get('title', 'Untitled')} (Score: {doc.get('relevance_score', 0)})")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
            
            print()
    
    except Exception as e:
        print(f"Error testing RAG agent: {e}")


def test_chatbot_supervisor():
    """Test the chatbot with supervisor coordination and session-based memory."""
    print("\n" + "="*60)
    print("TESTING CHATBOT SUPERVISOR WITH SESSION MEMORY")
    print("="*60)

    try:
        chatbot = EventsArticlesChatbot()
        session_id = "test_session_001"

        test_queries = [
            "How many events are in the database?",  # Should use SQL
            "Tell me about technology articles",      # Should use RAG
            "Show me recent events and related articles",  # Should use both
            "What's the latest information about AI?",     # Should use RAG
            "List all events with their dates"            # Should use SQL
        ]

        for i, query in enumerate(test_queries):
            print(f"\nQuery {i+1}: {query}")
            print("-" * 40)

            result = chatbot.chat(query, session_id=session_id)

            if result["success"]:
                print(f"Response: {result['response'][:500]}...")

                # Show metadata
                metadata = result.get("metadata", {})
                print(f"\nMetadata:")
                print(f"  Session ID: {result.get('session_id', 'unknown')}")
                print(f"  Route taken: {metadata.get('route_taken', 'unknown')}")
                print(f"  Agents used: {metadata.get('agents_used', [])}")
                print(f"  SQL results available: {metadata.get('sql_results_available', False)}")
                print(f"  RAG results available: {metadata.get('rag_results_available', False)}")

                # Show session metadata if available
                session_metadata = metadata.get('session_metadata', {})
                if session_metadata:
                    print(f"  Message count: {session_metadata.get('message_count', 0)}")
                    print(f"  Agents used in session: {session_metadata.get('agents_used', [])}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")

            print()

    except Exception as e:
        print(f"Error testing chatbot supervisor: {e}")


def test_system_status():
    """Test system status functionality."""
    print("\n" + "="*60)
    print("TESTING SYSTEM STATUS")
    print("="*60)
    
    try:
        chatbot = EventsArticlesChatbot()
        status = chatbot.get_system_status()
        
        print(f"Chatbot Status: {status.get('chatbot_status', 'unknown')}")
        print(f"Timestamp: {status.get('timestamp', 'unknown')}")
        
        components = status.get('components', {})
        print("\nComponent Status:")
        for component, status_info in components.items():
            print(f"  {component}: {status_info}")
        
        statistics = status.get('statistics', {})
        if statistics:
            print("\nStatistics:")
            for key, value in statistics.items():
                print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"Error testing system status: {e}")


def interactive_chat():
    """Interactive chat session for testing with session-based memory."""
    print("\n" + "="*60)
    print("INTERACTIVE CHAT SESSION WITH SESSION MEMORY")
    print("="*60)
    print("Type 'quit' to exit, 'status' for system status, 'history' for session history")

    try:
        chatbot = EventsArticlesChatbot()
        session_id = f"interactive_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Session ID: {session_id}")

        while True:
            query = input("\nYou: ").strip()

            if query.lower() == 'quit':
                break
            elif query.lower() == 'status':
                status = chatbot.get_system_status()
                print(f"\nSystem Status: {status.get('chatbot_status', 'unknown')}")
                continue
            elif query.lower() == 'history':
                history = chatbot.get_session_history(session_id)
                print(f"\nSession History ({len(history)} messages):")
                for msg in history[-5:]:  # Show last 5 messages
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')[:100]
                    agent = msg.get('agent', '')
                    agent_info = f" ({agent})" if agent else ""
                    print(f"  {role}{agent_info}: {content}...")
                continue
            elif not query:
                continue

            print("\nBot: Processing...")
            result = chatbot.chat(query, session_id=session_id)

            if result["success"]:
                print(f"Bot: {result['response']}")

                # Show which agents were used
                metadata = result.get("metadata", {})
                agents_used = metadata.get("agents_used", [])
                if agents_used:
                    print(f"(Used agents: {', '.join(agents_used)})")

                # Show session info
                session_metadata = metadata.get('session_metadata', {})
                if session_metadata:
                    msg_count = session_metadata.get('message_count', 0)
                    print(f"(Session messages: {msg_count})")
            else:
                print(f"Bot: Error - {result.get('error', 'Unknown error')}")

    except KeyboardInterrupt:
        print("\nChat session ended.")
    except Exception as e:
        print(f"Error in interactive chat: {e}")


def main():
    """Main test function."""
    print("Events Articles Chatbot - Agent Testing")
    print("="*60)
    
    # Check if we have the required environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY environment variable not set!")
        print("Some functionality may not work properly.")
        print()
    
    try:
        # Run individual agent tests
        test_sql_agent()
        test_rag_agent()
        test_chatbot_supervisor()
        test_system_status()
        
        # Ask if user wants interactive session
        response = input("\nWould you like to start an interactive chat session? (y/n): ")
        if response.lower().startswith('y'):
            interactive_chat()
    
    except Exception as e:
        logger.error(f"Error in main test function: {e}")
        print(f"Test failed with error: {e}")


if __name__ == "__main__":
    main()
