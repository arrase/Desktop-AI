"""Session management service for handling conversation history."""

import sqlite3
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

from ..core.constants import CONVERSATION_DB_PATH


class SessionInfo:
    """Information about a conversation session."""
    
    def __init__(self, session_id: str, created_at: str, updated_at: str, message_count: int = 0, first_message: str = ""):
        self.session_id = session_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.message_count = message_count
        self.first_message = first_message

    def get_display_name(self) -> str:
        """Get a user-friendly display name for the session."""
        if self.first_message:
            # Truncate first message to max 50 characters
            preview = self.first_message[:50]
            if len(self.first_message) > 50:
                preview += "..."
            return preview
        else:
            # Fallback to timestamp if no messages
            try:
                dt = datetime.fromisoformat(self.created_at.replace(' ', 'T'))
                return f"Conversation {dt.strftime('%d/%m %H:%M')}"
            except:
                return f"Conversation {self.session_id[:8]}"

    def get_relative_time(self) -> str:
        """Get a relative time description for the session."""
        try:
            dt = datetime.fromisoformat(self.created_at.replace(' ', 'T'))
            now = datetime.now()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "Just now"
        except:
            return "Unknown date"


class SessionService:
    """Service for managing conversation sessions and history."""
    
    def __init__(self, db_path: str = CONVERSATION_DB_PATH):
        self.db_path = db_path
        # Ensure the database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def get_all_sessions(self, limit: int = 50) -> List[SessionInfo]:
        """Get all conversation sessions, ordered by most recent update."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get sessions with message count and first user message
                query = """
                SELECT 
                    s.session_id,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id) as message_count,
                    (
                        SELECT m2.message_data 
                        FROM agent_messages m2 
                        WHERE m2.session_id = s.session_id 
                        ORDER BY m2.created_at ASC 
                        LIMIT 1
                    ) as first_message_data
                FROM agent_sessions s
                LEFT JOIN agent_messages m ON s.session_id = m.session_id
                GROUP BY s.session_id, s.created_at, s.updated_at
                ORDER BY s.updated_at DESC
                LIMIT ?
                """
                
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                
                sessions = []
                for row in rows:
                    session_id, created_at, updated_at, message_count, first_message_data = row
                    
                    # Extract first user message content
                    first_message = ""
                    if first_message_data:
                        try:
                            msg_json = json.loads(first_message_data)
                            if msg_json.get('role') == 'user':
                                first_message = msg_json.get('content', '')
                        except:
                            pass
                    
                    sessions.append(SessionInfo(
                        session_id=session_id,
                        created_at=created_at,
                        updated_at=updated_at,
                        message_count=message_count,
                        first_message=first_message
                    ))
                
                return sessions
                
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session and all its messages."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete messages first (due to foreign key constraint)
                cursor.execute("DELETE FROM agent_messages WHERE session_id = ?", (session_id,))
                # Delete session
                cursor.execute("DELETE FROM agent_sessions WHERE session_id = ?", (session_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False

    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get all messages for a specific session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT message_data FROM agent_messages WHERE session_id = ? ORDER BY created_at",
                    (session_id,)
                )
                rows = cursor.fetchall()
                
                messages = []
                for row in rows:
                    try:
                        msg_data = json.loads(row[0])
                        messages.append(msg_data)
                    except json.JSONDecodeError:
                        # Skip malformed messages
                        continue
                
                return messages
                
        except Exception as e:
            print(f"Error getting messages for session {session_id}: {e}")
            return []

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM agent_sessions WHERE session_id = ?", (session_id,))
                return cursor.fetchone() is not None
        except Exception:
            return False
