"""
Test runner for the Events Articles Chatbot.

This script properly sets up the Python path and runs various tests.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported correctly."""
    print("Testing imports...")
    
    try:
        from agents import EventsArticlesChatbot, AgentSupervisor, SessionMemory
        print("✅ Agents package imported successfully")
        
        from sql_agent.agent import SQLAgent
        print("✅ SQL Agent imported successfully")
        
        from rag_agent.agent import RAGAgent
        print("✅ RAG Agent imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_memory():
    """Test the session memory functionality."""
    print("\nTesting session memory...")
    
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
        print(f"✅ Retrieved {len(messages)} messages")
        
        if messages:
            print(f"   First message: {messages[0]['content'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Session memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_supervisor():
    """Test the agent supervisor."""
    print("\nTesting agent supervisor...")
    
    try:
        from agents.supervisor import AgentSupervisor
        
        supervisor = AgentSupervisor()
        print("✅ Agent supervisor created successfully")
        
        # Test basic functionality
        if supervisor.session_memory and supervisor.checkpointer:
            print("✅ Memory systems initialized")
        else:
            print("⚠️  Some memory systems not initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Supervisor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chatbot():
    """Test the main chatbot interface."""
    print("\nTesting chatbot interface...")
    
    try:
        from agents import EventsArticlesChatbot
        
        chatbot = EventsArticlesChatbot()
        print("✅ Chatbot created successfully")
        
        # Test system status
        status = chatbot.get_system_status()
        print(f"✅ System status: {status.get('chatbot_status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chatbot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_chat():
    """Test a simple chat interaction."""
    print("\nTesting simple chat interaction...")
    
    try:
        from agents import EventsArticlesChatbot
        
        chatbot = EventsArticlesChatbot()
        
        # Test a simple query
        response = chatbot.chat("Hello, can you help me?", session_id="test_session_001")
        
        print(f"Response success: {response.get('success')}")
        if response.get('success'):
            print(f"✅ Chat response: {response.get('response', 'No response')[:100]}...")
            
            # Test session history
            history = chatbot.get_session_history("test_session_001")
            print(f"✅ Session history: {len(history)} messages")
            
            return True
        else:
            print(f"❌ Chat failed: {response.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Events Articles Chatbot - Test Runner")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  WARNING: GOOGLE_API_KEY not set. Some functionality may not work.")
        print("   Set it with: export GOOGLE_API_KEY='your_key_here'")
        print()
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("Session Memory Test", test_session_memory),
        ("Supervisor Test", test_supervisor),
        ("Chatbot Test", test_chatbot),
        ("Simple Chat Test", test_simple_chat),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "="*50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
