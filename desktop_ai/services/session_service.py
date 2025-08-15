"""Simplified session service."""
import sqlite3
import json
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

from ..core import DATABASE_PATH


@dataclass
class SessionInfo:
    """Session information."""
    session_id: str
    created_at: str
    updated_at: str
    message_count: int = 0
    preview: str = ""

    def get_display_name(self) -> str:
        """Get display name."""
        if self.preview:
            return self.preview[:50] + ("..." if len(self.preview) > 50 else "")
        try:
            dt = datetime.fromisoformat(self.created_at.replace(' ', 'T'))
            return f"Conversation {dt.strftime('%d/%m %H:%M')}"
        except:
            return f"Session {self.session_id[:8]}"

    def get_relative_time(self) -> str:
        """Get relative time."""
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
            return "Unknown"


class SessionService:
    """Service for managing sessions."""
    
    def __init__(self):
        self.db_path = str(DATABASE_PATH)

    def get_sessions(self, limit: int = 50) -> List[SessionInfo]:
        """Get all sessions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
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
                    
                    preview = ""
                    if first_message_data:
                        try:
                            msg_json = json.loads(first_message_data)
                            if msg_json.get('role') == 'user':
                                preview = msg_json.get('content', '')
                        except:
                            pass
                    
                    sessions.append(SessionInfo(
                        session_id=session_id,
                        created_at=created_at,
                        updated_at=updated_at,
                        message_count=message_count,
                        preview=preview
                    ))
                
                return sessions
                
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM agent_messages WHERE session_id = ?", (session_id,))
                cursor.execute("DELETE FROM agent_sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False

    def get_messages(self, session_id: str) -> List[Dict]:
        """Get messages for a session."""
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
                        continue
                
                return messages
        except Exception as e:
            print(f"Error getting messages for session {session_id}: {e}")
            return []
