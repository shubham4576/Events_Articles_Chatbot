"""
Quick test script to verify the session memory fix.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_session_memory():
    """Test the custom session memory implementation."""
    print("Testing custom session memory...")
    
    try:
        from agents.memory import SessionMemory
        
        # Test in-memory storage
        memory = SessionMemory(":memory:")
        
        # Add a test message
        memory.add_message(
            session_id="test_session",
            role="user",
            content="Hello, this is a test message"
        )
        
        # Retrieve messages
        messages = memory.get_session_messages("test_session")
        print(f"Retrieved {len(messages)} messages")
        
        if messages:
            print(f"First message: {messages[0]}")
        
        print("✅ Session memory test passed")
        return True
        
    except Exception as e:
        print(f"❌ Session memory test failed: {e}")
        return False


def test_chatbot():
    """Test the chatbot with session memory."""
    print("\nTesting chatbot with session memory...")
    
    try:
        from agents import EventsArticlesChatbot
        
        chatbot = EventsArticlesChatbot()
        
        # Test a simple query
        response = chatbot.chat("Hello", session_id="test_session_123")
        
        print(f"Response success: {response.get('success')}")
        print(f"Response: {response.get('response', 'No response')[:100]}...")
        
        if response.get('success'):
            print("✅ Chatbot test passed")
            return True
        else:
            print(f"❌ Chatbot test failed: {response.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Chatbot test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Session Memory Fix Verification")
    print("=" * 40)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  WARNING: GOOGLE_API_KEY not set. Some functionality may not work.")
        print()
    
    # Run tests
    memory_ok = test_session_memory()
    chatbot_ok = test_chatbot()
    
    print("\n" + "=" * 40)
    if memory_ok and chatbot_ok:
        print("🎉 All tests passed! The session memory fix is working.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
