import sqlite3
import os
from datetime import datetime

# Pointing data storage explicitly inside buddy_chatbot/data
DB_PATH = os.path.join("data", "buddy_chat.db")

def init_db():
    """Creates the data directory and initializes database tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table to hold unique chat sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TEXT
        )
    ''')
    
    # Table to hold conversational message history logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            sender TEXT,
            message TEXT,
            timestamp TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(session_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_session(session_id):
    """Registers a brand new chat session into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO sessions (session_id, created_at) VALUES (?, ?)",
            (session_id, datetime.now().isoformat())
        )
        conn.commit()
    finally:
        conn.close()

def log_message(session_id, sender, message):
    """Logs a single conversation turn (User or Bot) to the local database file."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO messages (session_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, sender, message, datetime.now().isoformat())
        )
        conn.commit()
    finally:
        conn.close()

def load_chat_history(session_id):
    """Retrieves previous messages from SQLite to rebuild conversational memory."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sender, message FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for sender, message in rows:
        role = "user" if sender == "User" else "model"
        history.append({"role": role, "parts": [message]})
    return history
