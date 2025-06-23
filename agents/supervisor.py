"""
Agent Supervisor for coordinating between SQL and RAG agents with session-based memory.
"""

import logging
import os
from typing import Dict, Any, List, Literal
from pathlib import Path

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState, create_initial_state, update_session_metadata, get_session_context
from .config import DEFAULT_SUPERVISOR_CONFIG
from .memory import SessionMemory
from sql_agent.agent import SQLAgent
from rag_agent.agent import RAGAgent

logger = logging.getLogger(__name__)


class AgentSupervisor:
    """
    Supervisor agent that coordinates between SQL and RAG agents with session-based memory.

    The supervisor:
    1. Analyzes user queries to determine the best agent
    2. Routes queries to appropriate agents
    3. Combines results when needed
    4. Provides final responses to users
    5. Maintains session-based conversation memory using LangGraph
    """

    def __init__(self, config=None):
        """Initialize the Agent Supervisor with session-based memory."""
        self.config = config or DEFAULT_SUPERVISOR_CONFIG
        self.model = None
        self.sql_agent = None
        self.rag_agent = None
        self.graph = None
        self.checkpointer = None
        self.session_memory = None
        self._initialize_supervisor()
    
    def _initialize_supervisor(self):
        """Initialize the supervisor and all sub-agents with session-based memory."""
        try:
            # Initialize language model
            self.model = init_chat_model(
                self.config.model_name,
                model_provider=self.config.model_provider
            )

            # Initialize agents
            self.sql_agent = SQLAgent()
            self.rag_agent = RAGAgent()

            # Initialize memory checkpointer
            self._initialize_memory()

            # Build the workflow graph
            self._build_graph()

            logger.info("Agent Supervisor with session-based memory initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Agent Supervisor: {e}")
            raise

    def _initialize_memory(self):
        """Initialize the memory system for session-based persistence."""
        try:
            # Initialize custom session memory
            if self.config.use_persistent_memory and self.config.memory_backend == "sqlite":
                self.session_memory = SessionMemory(self.config.memory_db_path)
                logger.info("Initialized custom SQLite session memory")
            else:
                self.session_memory = SessionMemory(":memory:")
                logger.info("Initialized in-memory session storage")

            # Also initialize LangGraph's memory for graph state
            self.checkpointer = MemorySaver()
            logger.info("Initialized LangGraph memory saver")

        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}")
            # Fallback to in-memory for both
            self.session_memory = SessionMemory(":memory:")
            self.checkpointer = MemorySaver()
            logger.info("Fallback to in-memory storage")
    
    def _build_graph(self):
        """Build the LangGraph workflow for agent coordination."""
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("sql_agent", self._sql_agent_node)
        workflow.add_node("rag_agent", self._rag_agent_node)
        workflow.add_node("combiner", self._combiner_node)
        
        # Add edges
        workflow.set_entry_point("supervisor")
        
        # Conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_query,
            {
                "sql": "sql_agent",
                "rag": "rag_agent",
                "both": "sql_agent",  # Start with SQL, then go to RAG
                "end": END
            }
        )
        
        # From SQL agent
        workflow.add_conditional_edges(
            "sql_agent",
            self._after_sql_agent,
            {
                "rag": "rag_agent",
                "combiner": "combiner",
                "end": END
            }
        )
        
        # From RAG agent
        workflow.add_conditional_edges(
            "rag_agent",
            self._after_rag_agent,
            {
                "combiner": "combiner",
                "end": END
            }
        )
        
        # From combiner
        workflow.add_edge("combiner", END)
        
        # Compile the graph with session-based memory
        self.graph = workflow.compile(checkpointer=self.checkpointer)
    
    def _supervisor_node(self, state: AgentState) -> AgentState:
        """
        Supervisor node that analyzes the query and decides routing with session context.

        Args:
            state: Current agent state

        Returns:
            Updated state with routing decision
        """
        try:
            query = state["user_query"]
            session_id = state["session_id"]
            logger.info(f"Supervisor analyzing query for session {session_id}: {query}")

            # Get session context for better routing decisions
            session_context = get_session_context(state, self.config.context_window_size)

            # Analyze query to determine routing (with session context)
            routing_decision = self._analyze_query_with_context(query, session_context)

            state["route_to"] = routing_decision
            state["current_agent"] = "supervisor"

            # Update session metadata
            state = update_session_metadata(state, "supervisor")

            # Add supervisor message with session context
            supervisor_message = {
                "role": "supervisor",
                "content": f"Analyzing query and routing to: {routing_decision}",
                "agent": "supervisor",
                "session_id": session_id,
                "timestamp": state["session_metadata"]["last_activity"]
            }
            state["messages"].append(supervisor_message)

            # Store in session memory
            if self.session_memory:
                self.session_memory.add_message(
                    session_id=session_id,
                    role="supervisor",
                    content=f"Analyzing query and routing to: {routing_decision}",
                    agent="supervisor"
                )

            return state

        except Exception as e:
            logger.error(f"Error in supervisor node: {e}")
            state["route_to"] = "end"
            state["final_response"] = f"Error in query analysis: {str(e)}"
            return state
    
    def _sql_agent_node(self, state: AgentState) -> AgentState:
        """
        SQL agent node for database queries with session context.

        Args:
            state: Current agent state

        Returns:
            Updated state with SQL results
        """
        try:
            query = state["user_query"]
            session_id = state["session_id"]
            logger.info(f"SQL agent processing query for session {session_id}: {query}")

            # Get session context for better query understanding
            session_context = get_session_context(state, self.config.context_window_size)

            # Query SQL agent with session context
            sql_result = self.sql_agent.query(query)

            state["sql_results"] = sql_result
            state["current_agent"] = "sql"

            # Update session metadata
            state = update_session_metadata(state, "sql")

            # Add SQL agent message with session context
            sql_message = {
                "role": "assistant",
                "content": sql_result.get("response", "No response from SQL agent"),
                "agent": "sql",
                "session_id": session_id,
                "success": sql_result.get("success", False),
                "timestamp": state["session_metadata"]["last_activity"]
            }
            state["messages"].append(sql_message)

            # Store in session memory
            if self.session_memory:
                self.session_memory.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=sql_result.get("response", "No response from SQL agent"),
                    agent="sql",
                    metadata={"success": sql_result.get("success", False)}
                )

            return state

        except Exception as e:
            logger.error(f"Error in SQL agent node: {e}")
            state["sql_results"] = {
                "success": False,
                "error": str(e),
                "response": f"SQL agent error: {str(e)}"
            }
            return state
    
    def _rag_agent_node(self, state: AgentState) -> AgentState:
        """
        RAG agent node for semantic search with session context.

        Args:
            state: Current agent state

        Returns:
            Updated state with RAG results
        """
        try:
            query = state["user_query"]
            session_id = state["session_id"]
            logger.info(f"RAG agent processing query for session {session_id}: {query}")

            # Get session context for better semantic understanding
            session_context = get_session_context(state, self.config.context_window_size)

            # Query RAG agent with session context
            rag_result = self.rag_agent.query(query)

            state["rag_results"] = rag_result
            state["current_agent"] = "rag"

            # Update session metadata
            state = update_session_metadata(state, "rag")

            # Add RAG agent message with session context
            rag_message = {
                "role": "assistant",
                "content": rag_result.get("response", "No response from RAG agent"),
                "agent": "rag",
                "session_id": session_id,
                "success": rag_result.get("success", False),
                "timestamp": state["session_metadata"]["last_activity"]
            }
            state["messages"].append(rag_message)

            # Store in session memory
            if self.session_memory:
                self.session_memory.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=rag_result.get("response", "No response from RAG agent"),
                    agent="rag",
                    metadata={"success": rag_result.get("success", False)}
                )

            return state

        except Exception as e:
            logger.error(f"Error in RAG agent node: {e}")
            state["rag_results"] = {
                "success": False,
                "error": str(e),
                "response": f"RAG agent error: {str(e)}"
            }
            return state
    
    def _combiner_node(self, state: AgentState) -> AgentState:
        """
        Combiner node that synthesizes results from multiple agents.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with combined response
        """
        try:
            logger.info("Combining results from multiple agents")
            
            sql_results = state.get("sql_results")
            rag_results = state.get("rag_results")
            
            # Generate combined response
            combined_response = self._generate_combined_response(
                state["user_query"], sql_results, rag_results
            )
            
            state["final_response"] = combined_response
            state["current_agent"] = "combiner"
            
            # Add combiner message
            state["messages"].append({
                "role": "assistant",
                "content": combined_response,
                "agent": "combiner"
            })
            
            return state
            
        except Exception as e:
            logger.error(f"Error in combiner node: {e}")
            state["final_response"] = f"Error combining results: {str(e)}"
            return state
    
    def _analyze_query(self, query: str) -> Literal["sql", "rag", "both", "end"]:
        """
        Analyze user query to determine routing strategy.

        Args:
            query: User's query

        Returns:
            Routing decision
        """
        try:
            # Check if SQL agent thinks it can handle the query
            sql_relevant = self.sql_agent.is_sql_query(query)

            # Check if RAG agent thinks it can handle the query
            rag_relevant = self.rag_agent.is_rag_query(query)

            # Decision logic
            if sql_relevant and rag_relevant:
                return "both"
            elif sql_relevant:
                return "sql"
            elif rag_relevant:
                return "rag"
            else:
                # Default to RAG for general queries
                return "rag"

        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return "rag"  # Default fallback

    def _analyze_query_with_context(self, query: str, session_context: str) -> Literal["sql", "rag", "both", "end"]:
        """
        Analyze user query with session context to determine routing strategy.

        Args:
            query: User's current query
            session_context: Previous conversation context

        Returns:
            Routing decision with context consideration
        """
        try:
            # First, get basic routing decision
            basic_routing = self._analyze_query(query)

            # Analyze session context for patterns
            context_lower = session_context.lower()

            # If previous messages used SQL and current query might be follow-up
            if "sql" in context_lower and any(word in query.lower() for word in ["more", "also", "what about", "and"]):
                if basic_routing == "rag":
                    return "both"  # Combine with previous SQL context

            # If previous messages used RAG and current query might be follow-up
            if "rag" in context_lower and any(word in query.lower() for word in ["explain", "tell me more", "details"]):
                if basic_routing == "sql":
                    return "both"  # Combine with previous RAG context

            # Check for session continuity keywords
            continuity_keywords = ["continue", "more", "also", "additionally", "furthermore", "what else"]
            if any(keyword in query.lower() for keyword in continuity_keywords):
                # If there's context suggesting both types of information were useful
                if "sql" in context_lower and "rag" in context_lower:
                    return "both"

            return basic_routing

        except Exception as e:
            logger.error(f"Error analyzing query with context: {e}")
            return self._analyze_query(query)  # Fallback to basic analysis
    
    def _route_query(self, state: AgentState) -> str:
        """Route query based on supervisor decision."""
        return state.get("route_to", "end")
    
    def _after_sql_agent(self, state: AgentState) -> str:
        """Decide what to do after SQL agent."""
        route_to = state.get("route_to")
        
        if route_to == "both":
            return "rag"
        elif state.get("sql_results", {}).get("success"):
            return "end"
        else:
            return "rag"  # Try RAG if SQL failed
    
    def _after_rag_agent(self, state: AgentState) -> str:
        """Decide what to do after RAG agent."""
        route_to = state.get("route_to")
        
        if route_to == "both" and state.get("sql_results"):
            return "combiner"
        else:
            return "end"
    
    def _generate_combined_response(self, query: str, sql_results: Dict[str, Any], 
                                  rag_results: Dict[str, Any]) -> str:
        """Generate a combined response from both agents."""
        try:
            system_prompt = """
You are a response synthesizer that combines information from SQL database queries and semantic article search.

Your task is to create a comprehensive, coherent response that:
1. Integrates structured data from SQL queries with contextual information from articles
2. Provides a complete answer to the user's question
3. Maintains clarity and readability
4. Cites sources appropriately

Format your response to be helpful and informative, combining the best of both data sources.
            """.strip()
            
            user_prompt = f"""
User Question: {query}

SQL Results:
{sql_results.get('response', 'No SQL results') if sql_results else 'No SQL results'}

Article Search Results:
{rag_results.get('response', 'No article results') if rag_results else 'No article results'}

Please provide a comprehensive response that combines these information sources.
            """.strip()
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.model.invoke(messages)
            
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, dict) and 'content' in response:
                return response['content']
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error generating combined response: {e}")
            return f"I found information from both database and articles, but encountered an error combining them: {str(e)}"
    
    def process_query(self, user_query: str, session_id: str) -> Dict[str, Any]:
        """
        Process a user query through the agent system with session-based memory.

        Args:
            user_query: The user's question
            session_id: Session ID for conversation tracking and memory

        Returns:
            Dictionary containing the response and metadata
        """
        try:
            logger.info(f"Processing query for session {session_id}: {user_query}")

            # Store user message in session memory
            if self.session_memory:
                self.session_memory.add_message(
                    session_id=session_id,
                    role="user",
                    content=user_query
                )

            # Create initial state with session context
            initial_state = create_initial_state(user_query, session_id)

            # Load previous session messages into state
            if self.session_memory:
                previous_messages = self.session_memory.get_session_messages(session_id, limit=10)
                # Add previous messages to state (excluding the current user message we just added)
                initial_state["messages"] = previous_messages[:-1] if previous_messages else []

            # Run the graph with session-based memory
            config = {"configurable": {"thread_id": session_id}}
            final_state = self.graph.invoke(initial_state, config)

            # Extract final response
            final_response = final_state.get("final_response")
            if not final_response:
                # Get the last assistant message
                messages = final_state.get("messages", [])
                for message in reversed(messages):
                    if message.get("role") == "assistant":
                        final_response = message.get("content")
                        break

            return {
                "success": True,
                "response": final_response or "I couldn't generate a response to your query.",
                "sql_results": final_state.get("sql_results"),
                "rag_results": final_state.get("rag_results"),
                "route_taken": final_state.get("route_to"),
                "messages": final_state.get("messages", []),
                "session_id": session_id,
                "session_metadata": final_state.get("session_metadata", {})
            }

        except Exception as e:
            logger.error(f"Error processing query for session {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error processing your query: {str(e)}",
                "session_id": session_id
            }

    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversation history for a specific session.

        Args:
            session_id: Session ID to retrieve history for
            limit: Maximum number of messages to retrieve

        Returns:
            List of conversation messages
        """
        try:
            if self.session_memory:
                return self.session_memory.get_session_messages(session_id, limit)
            else:
                logger.warning("Session memory not initialized")
                return []

        except Exception as e:
            logger.error(f"Error getting session history for {session_id}: {e}")
            return []

    def clear_session_memory(self, session_id: str) -> bool:
        """
        Clear memory for a specific session.

        Args:
            session_id: Session ID to clear

        Returns:
            True if successful
        """
        try:
            if self.session_memory:
                success = self.session_memory.clear_session(session_id)
                if success:
                    logger.info(f"Cleared session memory for {session_id}")
                return success
            else:
                logger.warning("Session memory not initialized")
                return False

        except Exception as e:
            logger.error(f"Error clearing session memory for {session_id}: {e}")
            return False
