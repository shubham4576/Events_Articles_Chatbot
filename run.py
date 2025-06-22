#!/usr/bin/env python3
"""
Startup script for Events Articles Chatbot API
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if environment is properly configured."""
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("⚠️  .env file not found. Please copy .env.example to .env and configure it.")
        print("   cp .env.example .env")
        return False
    
    # Check if Google API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY not set in .env file.")
        print("   Please add your Google API key to the .env file.")
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "data/chromadb",
        "logs"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def main():
    """Main startup function."""
    print("🚀 Starting Events Articles Chatbot API...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Import and run the application
    try:
        import uvicorn
        from main import app
        
        print("✓ Environment configured")
        print("✓ Starting FastAPI server...")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/api/v1/health")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("   Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
