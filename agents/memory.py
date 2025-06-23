"""
Custom memory implementation for session-based conversation storage.
"""

import json
import sqlite3
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionMemory:
    """
    Custom session-based memory implementation using SQLite.
    
    This provides a simple alternative to LangGraph's checkpointer
    for storing conversation history by session.
    """
    
    def __init__(self, db_path: str = "data/session_memory.db"):
        """
        Initialize session memory with SQLite backend.

        Args:
            db_path: Path to SQLite database file or ":memory:" for in-memory
        """
        if db_path == ":memory:":
            self.db_path = ":memory:"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _get_db_path(self) -> str:
        """Get the database path as string for sqlite3.connect()."""
        return str(self.db_path) if self.db_path != ":memory:" else ":memory:"

    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self._get_db_path()) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS session_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        agent TEXT,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_session_id 
                    ON session_messages(session_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_session_timestamp 
                    ON session_messages(session_id, timestamp)
                """)
                
                conn.commit()
                logger.info(f"Initialized session memory database: {self._get_db_path()}")
                
        except Exception as e:
            logger.error(f"Failed to initialize session memory database: {e}")
            raise
    
    def add_message(self, session_id: str, role: str, content: str, 
                   agent: str = None, metadata: Dict[str, Any] = None):
        """
        Add a message to the session history.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, supervisor)
            content: Message content
            agent: Agent that generated the message (optional)
            metadata: Additional metadata (optional)
        """
        try:
            timestamp = datetime.now().isoformat()
            metadata_json = json.dumps(metadata) if metadata else None
            
            with sqlite3.connect(self._get_db_path()) as conn:
                conn.execute("""
                    INSERT INTO session_messages 
                    (session_id, role, content, agent, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session_id, role, content, agent, timestamp, metadata_json))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to add message to session {session_id}: {e}")
    
    def get_session_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        try:
            with sqlite3.connect(self._get_db_path()) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT role, content, agent, timestamp, metadata
                    FROM session_messages
                    WHERE session_id = ?
                    ORDER BY created_at ASC
                    LIMIT ?
                """, (session_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    message = {
                        "role": row["role"],
                        "content": row["content"],
                        "agent": row["agent"],
                        "timestamp": row["timestamp"],
                        "session_id": session_id
                    }
                    
                    # Parse metadata if present
                    if row["metadata"]:
                        try:
                            message["metadata"] = json.loads(row["metadata"])
                        except json.JSONDecodeError:
                            message["metadata"] = {}
                    
                    messages.append(message)
                
                return messages
                
        except Exception as e:
            logger.error(f"Failed to get messages for session {session_id}: {e}")
            return []
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear all messages for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self._get_db_path()) as conn:
                cursor = conn.execute("""
                    DELETE FROM session_messages WHERE session_id = ?
                """, (session_id,))
                
                conn.commit()
                deleted_count = cursor.rowcount
                
                logger.info(f"Cleared {deleted_count} messages from session {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to clear session {session_id}: {e}")
            return False
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session statistics
        """
        try:
            with sqlite3.connect(self._get_db_path()) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as message_count,
                        MIN(created_at) as first_message,
                        MAX(created_at) as last_message,
                        COUNT(DISTINCT agent) as agents_used
                    FROM session_messages
                    WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "message_count": row[0],
                        "first_message": row[1],
                        "last_message": row[2],
                        "agents_used_count": row[3]
                    }
                else:
                    return {
                        "message_count": 0,
                        "first_message": None,
                        "last_message": None,
                        "agents_used_count": 0
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get stats for session {session_id}: {e}")
            return {}
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up sessions older than specified days.
        
        Args:
            days_old: Number of days after which to delete sessions
            
        Returns:
            Number of messages deleted
        """
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
            
            with sqlite3.connect(self._get_db_path()) as conn:
                cursor = conn.execute("""
                    DELETE FROM session_messages 
                    WHERE created_at < ?
                """, (cutoff_date.isoformat(),))
                
                conn.commit()
                deleted_count = cursor.rowcount
                
                logger.info(f"Cleaned up {deleted_count} old messages")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0
