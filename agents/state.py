"""
Shared state management for the agent system with session-based memory.
"""

from typing import Annotated, Dict, List, Optional, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from datetime import datetime


class AgentState(TypedDict):
    """
    Shared state between all agents in the system with session-based memory.

    This state is passed between agents and contains:
    - messages: Conversation history with session context
    - session_id: Unique session identifier
    - current_agent: Which agent is currently active
    - sql_results: Results from SQL queries
    - rag_results: Results from RAG searches
    - user_query: Original user query
    - context: Additional context information including session data
    - next_action: What the supervisor should do next
    - session_metadata: Session-specific metadata
    """

    # Conversation messages with session context
    messages: Annotated[List[Dict[str, Any]], add_messages]

    # Session identification
    session_id: str

    # Current active agent
    current_agent: Optional[str]

    # User's original query
    user_query: str

    # Results from different agents
    sql_results: Optional[Dict[str, Any]]
    rag_results: Optional[Dict[str, Any]]

    # Additional context with session data
    context: Dict[str, Any]

    # Next action for supervisor
    next_action: Optional[str]

    # Agent routing decision
    route_to: Optional[str]

    # Final response
    final_response: Optional[str]

    # Session-specific metadata
    session_metadata: Dict[str, Any]


def create_initial_state(user_query: str, session_id: str) -> AgentState:
    """
    Create initial state for a new conversation with session context.

    Args:
        user_query: The user's query to process
        session_id: Unique session identifier

    Returns:
        Initial AgentState with session context
    """
    return AgentState(
        messages=[],
        session_id=session_id,
        current_agent=None,
        user_query=user_query,
        sql_results=None,
        rag_results=None,
        context={"session_id": session_id},
        next_action=None,
        route_to=None,
        final_response=None,
        session_metadata={
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0,
            "agents_used": []
        }
    )


def update_session_metadata(state: AgentState, agent_name: str = None) -> AgentState:
    """
    Update session metadata with current activity.

    Args:
        state: Current agent state
        agent_name: Name of the agent being used (optional)

    Returns:
        Updated state with refreshed metadata
    """
    state["session_metadata"]["last_activity"] = datetime.now().isoformat()
    state["session_metadata"]["message_count"] = len(state["messages"])

    if agent_name and agent_name not in state["session_metadata"]["agents_used"]:
        state["session_metadata"]["agents_used"].append(agent_name)

    return state


def get_session_context(state: AgentState, max_messages: int = 5) -> str:
    """
    Extract session context for agent processing.

    Args:
        state: Current agent state
        max_messages: Maximum number of previous messages to include

    Returns:
        Formatted session context string
    """
    messages = state.get("messages", [])
    if not messages:
        return "This is the start of a new conversation session."

    # Get recent messages for context
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

    context_parts = [f"Session ID: {state.get('session_id', 'unknown')}"]
    context_parts.append(f"Previous messages in this session:")

    for msg in recent_messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")[:100]  # Truncate long messages
        agent = msg.get("agent", "")
        agent_info = f" ({agent})" if agent else ""
        context_parts.append(f"  {role}{agent_info}: {content}...")

    return "\n".join(context_parts)
