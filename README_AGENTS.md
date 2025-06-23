# Events Articles Chatbot - Agent System with Session-Based Memory

This document describes the agent system implementation for the Events Articles Chatbot, including the SQL agent, RAG agent, and agent supervisor with LangGraph's session-based persistent memory.

## Architecture Overview

The chatbot uses a multi-agent architecture with LangGraph for coordination and persistent session memory:

```
User Query + Session ID
    ↓
Agent Supervisor (LangGraph StateGraph + Memory)
    ↓
┌─────────────┬─────────────┐
│ SQL Agent   │ RAG Agent   │
│ (Database)  │ (Semantic)  │
└─────────────┴─────────────┘
    ↓
Response Combiner (with Session Context)
    ↓
Final Response + Session Update
    ↓
Persistent Memory Storage (SQLite)
```

## Session-Based Memory

The system uses LangGraph's checkpointer system for persistent session memory:

- **Session Tracking**: Each conversation is tracked by a unique `session_id`
- **Persistent Storage**: Conversations are stored in SQLite database
- **Context Awareness**: Agents can access previous conversation context
- **Memory Management**: Automatic cleanup and session management

## Components

### 1. Agent Supervisor (`agents/supervisor.py`)

The supervisor coordinates between different agents using LangGraph's StateGraph:

- **Query Analysis**: Determines which agent(s) should handle the query
- **Routing Logic**: Routes queries to SQL, RAG, or both agents
- **Response Combination**: Combines results from multiple agents when needed
- **Error Handling**: Manages failures and fallbacks

**Routing Strategy:**
- SQL queries: Database-related questions (events, counts, dates, locations)
- RAG queries: Content-based questions (explanations, topics, concepts)
- Both: Complex queries requiring structured data and contextual information

### 2. SQL Agent (`sql_agent/agent.py`)

Handles structured database queries:

- **Database Access**: Queries SQLite database with events and articles tables
- **Query Generation**: Creates SQL queries from natural language
- **Result Formatting**: Formats database results for readability
- **Safety**: Prevents DML operations (INSERT, UPDATE, DELETE)

**Capabilities:**
- Count records, find specific events/articles
- Filter by dates, locations, authors
- Join tables for complex queries
- Aggregate data (counts, sums, averages)

### 3. RAG Agent (`rag_agent/agent.py`)

Handles semantic search and content-based queries:

- **Vector Search**: Uses ChromaDB with Gemini embeddings
- **Context Retrieval**: Finds relevant articles based on semantic similarity
- **Response Generation**: Creates contextual responses using retrieved content
- **Source Attribution**: Cites sources and provides relevance scores

**Capabilities:**
- Semantic search through article content
- Topic-based content discovery
- Contextual explanations and summaries
- Related content suggestions

### 4. Chatbot Interface (`agents/chatbot.py`)

Main interface for user interactions:

- **Conversation Management**: Handles chat sessions and history
- **User Context**: Maintains user-specific conversation threads
- **Response Formatting**: Formats responses for chat interfaces
- **System Monitoring**: Provides system status and health checks

## Usage

### Direct Agent Usage

```python
from sql_agent.agent import SQLAgent
from rag_agent.agent import RAGAgent

# SQL Agent
sql_agent = SQLAgent()
result = sql_agent.query("How many events are in the database?")

# RAG Agent
rag_agent = RAGAgent()
result = rag_agent.query("Tell me about artificial intelligence")
```

### Chatbot Interface with Session Memory

```python
from agents import EventsArticlesChatbot

chatbot = EventsArticlesChatbot()
session_id = "user123_session_001"

# First message in session
response1 = chatbot.chat("Show me recent events about technology", session_id=session_id)

# Follow-up message with context
response2 = chatbot.chat("Tell me more about the first event", session_id=session_id)

# Get session history
history = chatbot.get_session_history(session_id)
```

### API Endpoints with Session Support

The agents are exposed through FastAPI endpoints with session-based memory:

- `POST /api/v1/chat` - Chat with the bot (requires `session_id`)
- `GET /api/v1/chat/history/{session_id}` - Get session history
- `DELETE /api/v1/chat/memory/{session_id}` - Clear session memory
- `GET /api/v1/chat/status` - Get system status

#### Example API Usage

```bash
# Chat with session
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many events are there?", "session_id": "user123_session"}'

# Get session history
curl "http://localhost:8000/api/v1/chat/history/user123_session"

# Clear session memory
curl -X DELETE "http://localhost:8000/api/v1/chat/memory/user123_session"
```

## Configuration

### Environment Variables

```bash
GOOGLE_API_KEY=your_google_api_key_here
SQLITE_DB_PATH=data/events_articles.db
CHROMADB_PATH=data/chromadb
```

### Agent Settings

Agents use the existing configuration from `app/config/settings.py`:

- Database connection settings
- ChromaDB configuration
- Gemini API settings

## Testing

### Run Test Script

```bash
python examples/test_agents.py
```

This script tests:
- Individual agent functionality
- Supervisor coordination
- System status checks
- Interactive chat session

### API Testing

```bash
# Start the API server
python main.py

# Test chat endpoint
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many events are in the database?", "user_id": "test_user"}'

# Get system status
curl "http://localhost:8000/api/v1/chat/status"
```

## Query Examples

### SQL Agent Queries
- "How many events are in the database?"
- "Show me events happening in 2024"
- "List articles by author"
- "Find events in New York"
- "What's the most recent article?"

### RAG Agent Queries
- "Tell me about artificial intelligence"
- "Explain machine learning concepts"
- "What articles discuss technology trends?"
- "Find content about business strategies"
- "What information is available about sustainability?"

### Combined Queries
- "Show me recent events and related articles about AI"
- "Find technology events and explain the concepts"
- "List conferences about data science and provide background information"

## Error Handling

The system includes comprehensive error handling:

- **Agent Failures**: If one agent fails, the system tries alternatives
- **Database Errors**: SQL errors are caught and user-friendly messages provided
- **Vector Store Issues**: RAG failures fall back to database search when possible
- **API Errors**: All endpoints return structured error responses

## Performance Considerations

- **Lazy Loading**: Agents are initialized only when needed
- **Connection Pooling**: Database connections are managed efficiently
- **Caching**: Vector embeddings are cached in ChromaDB
- **Timeouts**: All operations have appropriate timeouts

## Extending the System

### Adding New Agents

1. Create agent class in new package (e.g., `web_agent/`)
2. Implement query method with consistent interface
3. Add routing logic to supervisor
4. Update state management if needed

### Custom Tools

Agents can be extended with custom tools:

```python
from langchain.tools import Tool

def custom_tool_function(query: str) -> str:
    # Custom logic here
    return result

custom_tool = Tool(
    name="CustomTool",
    description="Description of what the tool does",
    func=custom_tool_function
)

# Add to agent's tools list
```

### Monitoring and Logging

All agents include comprehensive logging:

- Query processing steps
- Agent routing decisions
- Performance metrics
- Error details

Logs can be configured through Python's logging system.

## Troubleshooting

### Common Issues

1. **Google API Key**: Ensure GOOGLE_API_KEY is set correctly
2. **Database Path**: Check that SQLite database exists and is accessible
3. **ChromaDB**: Verify ChromaDB directory permissions
4. **Dependencies**: Ensure all required packages are installed

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### System Status

Check system health:

```python
from agents import EventsArticlesChatbot
chatbot = EventsArticlesChatbot()
status = chatbot.get_system_status()
print(status)
```

## Future Enhancements

Potential improvements:

- **Memory Management**: Long-term conversation memory
- **User Preferences**: Personalized responses based on user history
- **Multi-modal**: Support for images and documents
- **Real-time Updates**: Live data synchronization
- **Analytics**: Usage analytics and performance monitoring
