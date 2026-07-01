import os
import sqlite3
import json
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "devpulse.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database schemas if they don't exist."""
    with get_connection() as conn:
        # Conversations Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT,
                tool_calls TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Active Repo Context Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repo_context (
                session_id TEXT PRIMARY KEY,
                repo_owner TEXT NOT NULL,
                repo_name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_message(session_id: str, role: str, content: str | None, tool_calls: list | None = None):
    """Save a chat message to history."""
    init_db()
    tool_calls_str = json.dumps(tool_calls) if tool_calls else None
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, tool_calls) VALUES (?, ?, ?, ?)",
            (session_id, role, content, tool_calls_str)
        )
        conn.commit()

def get_messages(session_id: str) -> list[dict]:
    """Retrieve chat history messages for a session."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT role, content, tool_calls FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,)
        )
        rows = cursor.fetchall()
        
    messages = []
    for r in rows:
        msg = {
            "role": r["role"],
            "content": r["content"]
        }
        if r["tool_calls"]:
            msg["tool_calls"] = json.loads(r["tool_calls"])
        messages.append(msg)
    return messages

def clear_history(session_id: str):
    """Clear chat messages and active repo context for a session."""
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM repo_context WHERE session_id = ?", (session_id,))
        conn.commit()

def set_repo_context(session_id: str, owner: str, repo: str):
    """Update active repository context for a session."""
    init_db()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO repo_context (session_id, repo_owner, repo_name, timestamp)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(session_id) DO UPDATE SET
                repo_owner=excluded.repo_owner,
                repo_name=excluded.repo_name,
                timestamp=CURRENT_TIMESTAMP
            """,
            (session_id, owner, repo)
        )
        conn.commit()

def get_repo_context(session_id: str) -> tuple[str, str] | None:
    """Retrieve active repository context (owner, repo) for a session."""
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT repo_owner, repo_name FROM repo_context WHERE session_id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
    if row:
        return row["repo_owner"], row["repo_name"]
    return None

# Auto-initialize database on import
init_db()
