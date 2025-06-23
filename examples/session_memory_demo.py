"""
Demo script showing session-based memory functionality.

This script demonstrates how the chatbot maintains conversation context
across multiple messages within a session.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents import EventsArticlesChatbot


def demo_session_memory():
    """Demonstrate session-based memory functionality."""
    print("Session-Based Memory Demo")
    print("=" * 50)
    
    try:
        # Initialize chatbot
        chatbot = EventsArticlesChatbot()
        session_id = f"demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"Session ID: {session_id}")
        print()
        
        # Conversation sequence to demonstrate memory
        conversation = [
            "How many events are in the database?",
            "What about articles?",
            "Tell me about the most recent event",
            "Can you explain more about that event?",
            "What articles are related to technology?",
            "Are there any events about the same topic?"
        ]
        
        for i, message in enumerate(conversation, 1):
            print(f"Message {i}: {message}")
            print("-" * 30)
            
            # Send message to chatbot
            response = chatbot.chat(message, session_id=session_id)
            
            if response["success"]:
                print(f"Bot: {response['response'][:300]}...")
                
                # Show session metadata
                metadata = response.get("metadata", {})
                session_metadata = metadata.get("session_metadata", {})
                
                print(f"\nSession Info:")
                print(f"  Message count: {session_metadata.get('message_count', 0)}")
                print(f"  Agents used: {metadata.get('agents_used', [])}")
                print(f"  Route taken: {metadata.get('route_taken', 'unknown')}")
                
            else:
                print(f"Error: {response.get('error', 'Unknown error')}")
            
            print("\n" + "="*50 + "\n")
        
        # Show session history
        print("SESSION HISTORY:")
        print("-" * 20)
        history = chatbot.get_session_history(session_id)
        
        for msg in history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]
            agent = msg.get('agent', '')
            agent_info = f" ({agent})" if agent else ""
            print(f"{role}{agent_info}: {content}...")
        
        print(f"\nTotal messages in session: {len(history)}")
        
        # Demonstrate session clearing
        print("\nClearing session memory...")
        success = chatbot.clear_session_memory(session_id)
        print(f"Session cleared: {success}")
        
        # Verify session is cleared
        history_after_clear = chatbot.get_session_history(session_id)
        print(f"Messages after clear: {len(history_after_clear)}")
        
    except Exception as e:
        print(f"Error in demo: {e}")


def demo_multiple_sessions():
    """Demonstrate multiple independent sessions."""
    print("\nMultiple Sessions Demo")
    print("=" * 50)
    
    try:
        chatbot = EventsArticlesChatbot()
        
        # Create two different sessions
        session1 = "session_tech"
        session2 = "session_business"
        
        # Session 1: Technology focus
        print("Session 1 (Technology):")
        response1 = chatbot.chat("Tell me about technology articles", session_id=session1)
        print(f"Response: {response1['response'][:200]}...")
        
        # Session 2: Business focus
        print("\nSession 2 (Business):")
        response2 = chatbot.chat("Show me business events", session_id=session2)
        print(f"Response: {response2['response'][:200]}...")
        
        # Continue Session 1 with context
        print("\nContinuing Session 1:")
        response3 = chatbot.chat("What about AI specifically?", session_id=session1)
        print(f"Response: {response3['response'][:200]}...")
        
        # Continue Session 2 with context
        print("\nContinuing Session 2:")
        response4 = chatbot.chat("Any networking events?", session_id=session2)
        print(f"Response: {response4['response'][:200]}...")
        
        # Show both session histories
        print("\nSession 1 History:")
        history1 = chatbot.get_session_history(session1)
        for msg in history1:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:80]
            print(f"  {role}: {content}...")
        
        print("\nSession 2 History:")
        history2 = chatbot.get_session_history(session2)
        for msg in history2:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:80]
            print(f"  {role}: {content}...")
        
        print(f"\nSession 1 messages: {len(history1)}")
        print(f"Session 2 messages: {len(history2)}")
        
    except Exception as e:
        print(f"Error in multiple sessions demo: {e}")


def demo_context_awareness():
    """Demonstrate how agents use session context for better responses."""
    print("\nContext Awareness Demo")
    print("=" * 50)
    
    try:
        chatbot = EventsArticlesChatbot()
        session_id = "context_demo"
        
        # Build context gradually
        messages = [
            ("How many events are there?", "Establishing baseline"),
            ("What about recent ones?", "Building on previous query"),
            ("Show me details about the first one", "Referencing previous results"),
            ("Any articles about similar topics?", "Cross-referencing with articles"),
            ("Compare that with the event data", "Combining both data sources")
        ]
        
        for message, explanation in messages:
            print(f"Query: {message}")
            print(f"Context: {explanation}")
            print("-" * 30)
            
            response = chatbot.chat(message, session_id=session_id)
            
            if response["success"]:
                print(f"Response: {response['response'][:250]}...")
                
                metadata = response.get("metadata", {})
                print(f"Route: {metadata.get('route_taken', 'unknown')}")
                print(f"Agents: {metadata.get('agents_used', [])}")
                
            print("\n" + "="*40 + "\n")
        
    except Exception as e:
        print(f"Error in context awareness demo: {e}")


def main():
    """Run all demos."""
    print("Events Articles Chatbot - Session Memory Demonstrations")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY not set. Some functionality may not work.")
        print()
    
    try:
        # Run demos
        demo_session_memory()
        demo_multiple_sessions()
        demo_context_awareness()
        
        print("\nAll demos completed successfully!")
        
    except Exception as e:
        print(f"Demo failed: {e}")


if __name__ == "__main__":
    main()
