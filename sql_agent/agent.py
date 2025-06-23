"""
Enhanced SQL Agent for querying the events and articles database.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from app.config import settings

logger = logging.getLogger(__name__)


class SQLAgent:
    """
    Enhanced SQL Agent for querying events and articles database.
    
    This agent can:
    - Query events and articles tables
    - Provide structured responses
    - Handle complex queries with joins
    - Format results for better readability
    """
    
    def __init__(self):
        """Initialize the SQL Agent."""
        self.model = None
        self.db = None
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the SQL agent with database connection and tools."""
        try:
            # Initialize the language model
            self.model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
            
            # Get database path
            base_dir = Path(__file__).resolve().parent.parent
            sqlite_path = base_dir / "data" / "events_articles.db"
            
            # Initialize database connection
            self.db = SQLDatabase.from_uri(f"sqlite:///{sqlite_path}")
            
            # Create SQL toolkit
            toolkit = SQLDatabaseToolkit(db=self.db, llm=self.model)
            tools = toolkit.get_tools()
            
            # Enhanced system prompt
            system_prompt = self._get_system_prompt()
            
            # Create the agent
            self.agent = create_react_agent(
                self.model,
                tools,
                prompt=system_prompt,
            )
            
            logger.info("SQL Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SQL Agent: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the SQL agent."""
        return f"""
You are a specialized SQL agent for querying an events and articles database.

DATABASE SCHEMA:
- events table: Contains event information (post_title, post_content, event_date, location, etc.)
- articles table: Contains article information (post_title, post_content, keywords, descriptions, etc.)

INSTRUCTIONS:
1. Always start by examining the database schema to understand available tables and columns
2. Create syntactically correct {self.db.dialect} queries
3. Limit results to at most 10 unless user specifies otherwise
4. Order results by relevance (e.g., recent dates for events, relevance for articles)
5. Only query relevant columns, never SELECT *
6. Double-check queries before execution
7. If a query fails, analyze the error and retry with corrections
8. Provide clear, formatted responses with context

RESTRICTIONS:
- NO DML statements (INSERT, UPDATE, DELETE, DROP)
- NO schema modifications
- Always use LIMIT to prevent large result sets

RESPONSE FORMAT:
- Provide a brief summary of what you found
- Include relevant details from the query results
- If no results, suggest alternative searches
- Format data in a readable way

Remember: You're helping users find information about events and articles. Be helpful and informative!
        """.strip()
    
    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a user query and return structured results.
        
        Args:
            user_query: The user's natural language query
            
        Returns:
            Dictionary containing query results and metadata
        """
        try:
            logger.info(f"Processing SQL query: {user_query}")
            
            # Invoke the agent
            result = self.agent.invoke({"messages": [("user", user_query)]})
            
            # Extract the response
            response_content = ""
            if result and "messages" in result:
                for message in result["messages"]:
                    if hasattr(message, 'content'):
                        response_content += message.content + "\n"
                    elif isinstance(message, dict) and "content" in message:
                        response_content += message["content"] + "\n"
            
            return {
                "success": True,
                "response": response_content.strip(),
                "agent_type": "sql",
                "query": user_query,
                "raw_result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing SQL query: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_type": "sql",
                "query": user_query,
                "response": f"I encountered an error while querying the database: {str(e)}"
            }
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the database schema.
        
        Returns:
            Dictionary containing database schema information
        """
        try:
            if not self.db:
                return {"error": "Database not initialized"}
            
            # Get table names
            tables = self.db.get_usable_table_names()
            
            # Get schema for each table
            schema_info = {}
            for table in tables:
                try:
                    schema_info[table] = self.db.get_table_info([table])
                except Exception as e:
                    schema_info[table] = f"Error getting schema: {e}"
            
            return {
                "tables": tables,
                "schema": schema_info,
                "dialect": self.db.dialect
            }
            
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {"error": str(e)}
    
    def is_sql_query(self, query: str) -> bool:
        """
        Determine if a query is likely to need SQL database access.
        
        Args:
            query: User query to analyze
            
        Returns:
            True if query likely needs SQL access
        """
        sql_keywords = [
            "event", "events", "when", "where", "date", "time", "location",
            "article", "articles", "author", "company", "booth", "contact",
            "count", "how many", "list", "show", "find", "search",
            "recent", "upcoming", "past", "latest", "oldest"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in sql_keywords)
