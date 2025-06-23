# Events Articles Chatbot

A sophisticated multi-agent chatbot system built with LangGraph that combines SQL database queries and semantic search to provide comprehensive responses about events and articles.

## Features

- **Multi-Agent Architecture**: Coordinates between SQL and RAG agents using LangGraph
- **SQL Agent**: Queries structured data from SQLite database (events and articles)
- **RAG Agent**: Performs semantic search using ChromaDB and Gemini embeddings
- **Agent Supervisor**: Intelligently routes queries and combines results
- **FastAPI Integration**: RESTful API endpoints for chat functionality
- **Conversation Management**: Maintains chat history and user sessions
- **Real-time Data**: Fetches and processes data from external APIs

## Architecture

```
User Query → Agent Supervisor → SQL Agent / RAG Agent → Response Combiner → Final Response
```

The system uses LangGraph's StateGraph to coordinate between agents based on query analysis.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export GOOGLE_API_KEY="your_google_api_key_here"
```

### 3. Initialize Database

```bash
python main.py
```

### 4. Test the Agents

```bash
python examples/test_agents.py
```

## Usage

### API Endpoints

Start the server:
```bash
python main.py
```

Chat with the bot:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many events are in the database?", "user_id": "user123"}'
```

### Direct Agent Usage

```python
from agents import EventsArticlesChatbot

# Initialize chatbot
chatbot = EventsArticlesChatbot()

# Chat with the bot
response = chatbot.chat("Show me recent technology events", user_id="user123")
print(response["response"])
```

## Documentation

- [API Documentation](README_API.md) - FastAPI endpoints and data management
- [Agent System](README_AGENTS.md) - Detailed agent architecture and usage
- [Database Schema](DATABASE_SCHEMA.md) - Database structure and relationships

## Project Structure

```
├── agents/                 # Multi-agent system
│   ├── supervisor.py      # Agent coordinator using LangGraph
│   ├── chatbot.py         # Main chatbot interface
│   ├── state.py           # Shared state management
│   └── config.py          # Agent configurations
├── sql_agent/             # SQL database agent
│   ├── agent.py           # Enhanced SQL agent
│   └── utility/           # SQL utilities
├── rag_agent/             # RAG semantic search agent
│   └── agent.py           # RAG implementation
├── app/                   # FastAPI application
│   ├── api/               # API endpoints
│   ├── database/          # Database operations
│   ├── models/            # Data models and schemas
│   └── services/          # External services
├── examples/              # Example scripts and tests
└── data/                  # Database and vector store
```

## Technologies

- **LangGraph**: Agent coordination and workflow management
- **LangChain**: Agent framework and tools
- **Google Gemini**: Language model and embeddings
- **ChromaDB**: Vector database for semantic search
- **SQLite**: Structured data storage
- **FastAPI**: REST API framework
- **SQLAlchemy**: Database ORM
