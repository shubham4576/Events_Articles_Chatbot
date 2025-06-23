"""
Configuration settings for the agent system.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for individual agents."""
    
    # Model settings
    model_name: str = "gemini-2.0-flash"
    model_provider: str = "google_genai"
    temperature: float = 0.1
    max_tokens: int = 2000
    
    # Timeout settings
    query_timeout: int = 30  # seconds
    model_timeout: int = 60  # seconds
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds


@dataclass
class SQLAgentConfig(AgentConfig):
    """Configuration specific to SQL Agent."""
    
    # Query limits
    default_limit: int = 10
    max_limit: int = 100
    
    # Safety settings
    allow_dml: bool = False  # Never allow DML operations
    allowed_tables: List[str] = None  # None means all tables allowed
    
    # Query optimization
    explain_queries: bool = False
    query_cache_size: int = 100


@dataclass
class RAGAgentConfig(AgentConfig):
    """Configuration specific to RAG Agent."""
    
    # Search settings
    default_n_results: int = 5
    max_n_results: int = 20
    min_relevance_score: float = 0.3
    
    # Context settings
    max_context_length: int = 4000  # characters
    context_overlap: int = 200  # characters
    
    # Response generation
    include_sources: bool = True
    max_source_preview: int = 200  # characters


@dataclass
class SupervisorConfig(AgentConfig):
    """Configuration for the Agent Supervisor."""

    # Routing settings
    routing_confidence_threshold: float = 0.7
    fallback_to_rag: bool = True  # Fallback to RAG if SQL fails

    # Combination settings
    combine_results_threshold: int = 2  # Minimum agents for combination
    max_combined_response_length: int = 2000  # characters

    # Session-based Memory settings
    conversation_memory_size: int = 10  # messages per session
    context_window_size: int = 5  # previous messages to consider
    session_timeout: int = 3600  # seconds (1 hour)
    max_sessions: int = 1000  # maximum concurrent sessions
    memory_cleanup_interval: int = 300  # seconds (5 minutes)

    # LangGraph Memory settings
    use_persistent_memory: bool = True
    memory_backend: str = "sqlite"  # "memory" or "sqlite"
    memory_db_path: str = "data/langgraph_memory.db"


@dataclass
class ChatbotConfig:
    """Configuration for the main chatbot interface."""
    
    # Conversation settings
    max_conversation_history: int = 100  # messages per user
    conversation_timeout: int = 3600  # seconds (1 hour)
    
    # User management
    max_concurrent_users: int = 100
    user_session_timeout: int = 1800  # seconds (30 minutes)
    
    # Response formatting
    max_response_length: int = 2000  # characters
    include_metadata: bool = True
    include_timing: bool = False


# Default configurations
DEFAULT_SQL_CONFIG = SQLAgentConfig()
DEFAULT_RAG_CONFIG = RAGAgentConfig()
DEFAULT_SUPERVISOR_CONFIG = SupervisorConfig()
DEFAULT_CHATBOT_CONFIG = ChatbotConfig()


def get_agent_config(agent_type: str) -> AgentConfig:
    """
    Get configuration for a specific agent type.
    
    Args:
        agent_type: Type of agent ('sql', 'rag', 'supervisor', 'chatbot')
        
    Returns:
        Appropriate configuration object
    """
    configs = {
        'sql': DEFAULT_SQL_CONFIG,
        'rag': DEFAULT_RAG_CONFIG,
        'supervisor': DEFAULT_SUPERVISOR_CONFIG,
        'chatbot': DEFAULT_CHATBOT_CONFIG
    }
    
    return configs.get(agent_type, AgentConfig())


def update_config_from_env() -> Dict[str, Any]:
    """
    Update configurations from environment variables.
    
    Returns:
        Dictionary of updated configuration values
    """
    import os
    
    updates = {}
    
    # Model settings
    if os.getenv('AGENT_MODEL_NAME'):
        updates['model_name'] = os.getenv('AGENT_MODEL_NAME')
    
    if os.getenv('AGENT_TEMPERATURE'):
        try:
            updates['temperature'] = float(os.getenv('AGENT_TEMPERATURE'))
        except ValueError:
            pass
    
    # Timeout settings
    if os.getenv('AGENT_QUERY_TIMEOUT'):
        try:
            updates['query_timeout'] = int(os.getenv('AGENT_QUERY_TIMEOUT'))
        except ValueError:
            pass
    
    # SQL specific
    if os.getenv('SQL_AGENT_DEFAULT_LIMIT'):
        try:
            updates['sql_default_limit'] = int(os.getenv('SQL_AGENT_DEFAULT_LIMIT'))
        except ValueError:
            pass
    
    # RAG specific
    if os.getenv('RAG_AGENT_DEFAULT_RESULTS'):
        try:
            updates['rag_default_n_results'] = int(os.getenv('RAG_AGENT_DEFAULT_RESULTS'))
        except ValueError:
            pass
    
    if os.getenv('RAG_AGENT_MIN_SCORE'):
        try:
            updates['rag_min_relevance_score'] = float(os.getenv('RAG_AGENT_MIN_SCORE'))
        except ValueError:
            pass
    
    return updates


# Agent routing keywords for the supervisor
SQL_KEYWORDS = [
    'count', 'how many', 'number of', 'total', 'sum',
    'list', 'show', 'display', 'find all',
    'event', 'events', 'article', 'articles',
    'date', 'time', 'when', 'where', 'location',
    'author', 'user', 'company', 'contact',
    'recent', 'latest', 'oldest', 'first', 'last',
    'filter', 'search by', 'with', 'having'
]

RAG_KEYWORDS = [
    'about', 'explain', 'tell me', 'what is', 'what are',
    'how does', 'how do', 'why', 'because',
    'describe', 'definition', 'meaning',
    'concept', 'idea', 'topic', 'subject',
    'similar', 'related', 'like', 'compare',
    'information', 'details', 'content',
    'understand', 'learn', 'know'
]

COMBINED_KEYWORDS = [
    'and', 'also', 'plus', 'additionally',
    'both', 'together', 'combined',
    'as well as', 'along with',
    'comprehensive', 'complete', 'full'
]


def classify_query_intent(query: str) -> str:
    """
    Classify query intent based on keywords.
    
    Args:
        query: User query to classify
        
    Returns:
        Intent classification ('sql', 'rag', 'both', 'unknown')
    """
    query_lower = query.lower()
    
    sql_score = sum(1 for keyword in SQL_KEYWORDS if keyword in query_lower)
    rag_score = sum(1 for keyword in RAG_KEYWORDS if keyword in query_lower)
    combined_score = sum(1 for keyword in COMBINED_KEYWORDS if keyword in query_lower)
    
    # If combined keywords are present, likely needs both agents
    if combined_score > 0 and (sql_score > 0 or rag_score > 0):
        return 'both'
    
    # If both types of keywords are present
    if sql_score > 0 and rag_score > 0:
        return 'both'
    
    # If primarily SQL keywords
    if sql_score > rag_score and sql_score > 0:
        return 'sql'
    
    # If primarily RAG keywords
    if rag_score > sql_score and rag_score > 0:
        return 'rag'
    
    # Default to RAG for general queries
    return 'rag'
