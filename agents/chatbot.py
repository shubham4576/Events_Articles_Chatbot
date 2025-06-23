"""
Main chatbot interface that uses the agent supervisor.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain.schema import HumanMessage, AIMessage, SystemMessage

try:
    from .supervisor import AgentSupervisor
except ImportError:
    # Absolute import for direct execution
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    from agents.supervisor import AgentSupervisor

logger = logging.getLogger(__name__)


class EventsArticlesChatbot:
    """
    Main chatbot interface for the Events Articles system.
    
    This chatbot:
    - Provides a simple interface for users to ask questions
    - Uses the agent supervisor to coordinate responses
    - Maintains conversation history
    - Handles different types of queries (SQL, RAG, combined)
    """
    
    def __init__(self):
        """Initialize the chatbot with session-based memory."""
        self.supervisor = None
        self._initialize_chatbot()
    
    def _initialize_chatbot(self):
        """Initialize the chatbot with agent supervisor."""
        try:
            self.supervisor = AgentSupervisor()
            logger.info("Events Articles Chatbot initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {e}")
            raise
    
    def chat(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process a chat message and return response with session-based memory.

        Args:
            message: User's message/question
            session_id: Session ID for conversation tracking and memory

        Returns:
            Dictionary containing response and metadata
        """
        try:
            logger.info(f"Processing chat message for session {session_id}: {message}")

            # Process the query through the supervisor with session-based memory
            result = self.supervisor.process_query(message, session_id)

            # Format response for chat interface
            chat_response = {
                "response": result.get("response", "I couldn't process your request."),
                "success": result.get("success", False),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "route_taken": result.get("route_taken"),
                    "agents_used": self._extract_agents_used(result),
                    "sql_results_available": bool(result.get("sql_results")),
                    "rag_results_available": bool(result.get("rag_results")),
                    "session_metadata": result.get("session_metadata", {})
                }
            }

            # Add error information if present
            if not result.get("success") and result.get("error"):
                chat_response["error"] = result["error"]

            return chat_response

        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return {
                "response": f"I encountered an error processing your message: {str(e)}",
                "success": False,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session using LangGraph memory.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve

        Returns:
            List of conversation messages
        """
        try:
            logger.info(f"Getting session history for {session_id}")

            # Get history from supervisor's memory system
            history = self.supervisor.get_session_history(session_id, limit)

            # Format history for API response
            formatted_history = []
            for msg in history:
                # Keep original roles from session memory (not LangGraph converted ones)
                formatted_msg = {
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", ""),
                    "agent": msg.get("agent", ""),
                    "session_id": session_id
                }
                formatted_history.append(formatted_msg)

            return formatted_history

        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []
    
    def clear_session_memory(self, session_id: str) -> bool:
        """
        Clear session memory using LangGraph's memory system.

        Args:
            session_id: Session identifier to clear

        Returns:
            True if successful
        """
        try:
            logger.info(f"Clearing session memory for {session_id}")

            # Clear session memory from supervisor's memory system
            success = self.supervisor.clear_session_memory(session_id)

            if success:
                logger.info(f"Successfully cleared session memory for {session_id}")
            else:
                logger.warning(f"Failed to clear session memory for {session_id}")

            return success

        except Exception as e:
            logger.error(f"Error clearing session memory: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status and health information.
        
        Returns:
            Dictionary containing system status
        """
        try:
            status = {
                "chatbot_status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {}
            }
            
            # Check supervisor
            if self.supervisor:
                status["components"]["supervisor"] = "initialized"
                
                # Check SQL agent
                try:
                    if self.supervisor.sql_agent:
                        db_info = self.supervisor.sql_agent.get_database_info()
                        if "error" not in db_info:
                            status["components"]["sql_agent"] = "healthy"
                            status["components"]["database_tables"] = db_info.get("tables", [])
                        else:
                            status["components"]["sql_agent"] = f"error: {db_info['error']}"
                    else:
                        status["components"]["sql_agent"] = "not_initialized"
                except Exception as e:
                    status["components"]["sql_agent"] = f"error: {str(e)}"
                
                # Check RAG agent
                try:
                    if self.supervisor.rag_agent and self.supervisor.rag_agent.vector_store:
                        status["components"]["rag_agent"] = "healthy"
                        status["components"]["vector_store"] = "connected"
                    else:
                        status["components"]["rag_agent"] = "not_initialized"
                except Exception as e:
                    status["components"]["rag_agent"] = f"error: {str(e)}"
            else:
                status["chatbot_status"] = "error"
                status["components"]["supervisor"] = "not_initialized"
            
            # Add session statistics (simplified since we use LangGraph memory)
            status["statistics"] = {
                "memory_backend": "langgraph_persistent",
                "session_based_memory": True
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "chatbot_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    

    
    def _extract_agents_used(self, result: Dict[str, Any]) -> List[str]:
        """Extract which agents were used from the result."""
        agents_used = []
        
        if result.get("sql_results"):
            agents_used.append("sql")
        
        if result.get("rag_results"):
            agents_used.append("rag")
        
        # Check messages for agent information
        messages = result.get("messages", [])
        for message in messages:
            agent = None
            if isinstance(message, dict):
                agent = message.get("agent")
            elif hasattr(message, "agent"):
                agent = getattr(message, "agent", None)
            # else: could be HumanMessage without agent attribute
            if agent and agent not in agents_used:
                agents_used.append(agent)
        
        return agents_used
