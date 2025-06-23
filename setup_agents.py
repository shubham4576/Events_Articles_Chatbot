"""
Setup script for the Events Articles Chatbot agent system.

This script initializes and verifies all components of the agent system.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def check_environment():
    """Check if required environment variables are set."""
    print("Checking environment variables...")
    
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}='your_value_here'")
        return False
    else:
        print("✅ All required environment variables are set")
        return True


def check_dependencies():
    """Check if required Python packages are installed."""
    print("\nChecking Python dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "chromadb", 
        "google-generativeai", "langchain", "langgraph",
        "pydantic", "httpx"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("\nPlease install missing packages:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All required packages are installed")
        return True


def check_database():
    """Check if database directory and files exist."""
    print("\nChecking database setup...")
    
    data_dir = Path("data")
    db_file = data_dir / "events_articles.db"
    chromadb_dir = data_dir / "chromadb"
    
    # Create directories if they don't exist
    data_dir.mkdir(exist_ok=True)
    chromadb_dir.mkdir(exist_ok=True)
    
    print(f"✅ Data directory: {data_dir.absolute()}")
    print(f"✅ ChromaDB directory: {chromadb_dir.absolute()}")
    
    if db_file.exists():
        print(f"✅ SQLite database found: {db_file.absolute()}")
    else:
        print(f"⚠️  SQLite database not found: {db_file.absolute()}")
        print("   Database will be created when the application starts")
    
    return True


def test_sql_agent():
    """Test SQL agent initialization."""
    print("\nTesting SQL Agent...")
    
    try:
        from sql_agent.agent import SQLAgent
        
        sql_agent = SQLAgent()
        db_info = sql_agent.get_database_info()
        
        if "error" in db_info:
            print(f"❌ SQL Agent error: {db_info['error']}")
            return False
        else:
            tables = db_info.get("tables", [])
            print(f"✅ SQL Agent initialized successfully")
            print(f"   Available tables: {', '.join(tables) if tables else 'None'}")
            return True
            
    except Exception as e:
        print(f"❌ SQL Agent initialization failed: {e}")
        return False


def test_rag_agent():
    """Test RAG agent initialization."""
    print("\nTesting RAG Agent...")
    
    try:
        from rag_agent.agent import RAGAgent
        
        rag_agent = RAGAgent()
        
        # Test if vector store is accessible
        if rag_agent.vector_store and rag_agent.vector_store.collection:
            print("✅ RAG Agent initialized successfully")
            print("   Vector store connection established")
            return True
        else:
            print("❌ RAG Agent vector store not accessible")
            return False
            
    except Exception as e:
        print(f"❌ RAG Agent initialization failed: {e}")
        return False


def test_supervisor():
    """Test agent supervisor initialization."""
    print("\nTesting Agent Supervisor...")
    
    try:
        from agents.supervisor import AgentSupervisor
        
        supervisor = AgentSupervisor()
        
        if supervisor.sql_agent and supervisor.rag_agent and supervisor.graph:
            print("✅ Agent Supervisor initialized successfully")
            print("   All sub-agents are ready")
            return True
        else:
            print("❌ Agent Supervisor initialization incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Agent Supervisor initialization failed: {e}")
        return False


def test_chatbot():
    """Test main chatbot interface."""
    print("\nTesting Chatbot Interface...")
    
    try:
        from agents import EventsArticlesChatbot
        
        chatbot = EventsArticlesChatbot()
        status = chatbot.get_system_status()
        
        if status.get("chatbot_status") == "healthy":
            print("✅ Chatbot interface initialized successfully")
            print("   System status: healthy")
            return True
        else:
            print(f"❌ Chatbot status: {status.get('chatbot_status', 'unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Chatbot initialization failed: {e}")
        return False


def run_quick_test():
    """Run a quick end-to-end test."""
    print("\nRunning quick end-to-end test...")
    
    try:
        from agents import EventsArticlesChatbot
        
        chatbot = EventsArticlesChatbot()
        
        # Test a simple query
        test_query = "Hello, can you help me?"
        response = chatbot.chat(test_query, user_id="setup_test")
        
        if response.get("success"):
            print("✅ End-to-end test successful")
            print(f"   Test query: '{test_query}'")
            print(f"   Response received: {len(response.get('response', ''))} characters")
            return True
        else:
            print(f"❌ End-to-end test failed: {response.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("Events Articles Chatbot - Agent System Setup")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Run all checks
    checks = [
        ("Environment Variables", check_environment),
        ("Python Dependencies", check_dependencies),
        ("Database Setup", check_database),
        ("SQL Agent", test_sql_agent),
        ("RAG Agent", test_rag_agent),
        ("Agent Supervisor", test_supervisor),
        ("Chatbot Interface", test_chatbot),
        ("End-to-End Test", run_quick_test)
    ]
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_checks_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed with exception: {e}")
            all_checks_passed = False
    
    print("\n" + "=" * 60)
    
    if all_checks_passed:
        print("🎉 All checks passed! The agent system is ready to use.")
        print("\nNext steps:")
        print("1. Start the API server: python main.py")
        print("2. Test the agents: python examples/test_agents.py")
        print("3. Access the API docs: http://localhost:8000/docs")
    else:
        print("❌ Some checks failed. Please fix the issues above before proceeding.")
        print("\nFor help, check:")
        print("- README_AGENTS.md for detailed setup instructions")
        print("- README_API.md for API documentation")
        sys.exit(1)


if __name__ == "__main__":
    main()
