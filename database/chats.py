"""
database/chats.py
Per-user chat history persistence.
"""

from __future__ import annotations
from datetime import datetime
from database.connection import get_db

MAX_HISTORY = 100  # cap stored messages per user


def save_message(username: str, role: str, content: str) -> None:
    """Append a message to the user's chat history."""
    db = get_db()
    msg = {
        "role": role,          # "user" | "assistant"
        "content": content,
        "ts": datetime.utcnow().isoformat(),
    }
    db["chats"].update_one(
        {"username": username},
        {"$push": {"messages": msg}},
        upsert=True,
    )


def get_history(username: str, limit: int = 20) -> list[dict]:
    """Return the last `limit` messages for the user."""
    db = get_db()
    doc = db["chats"].find_one({"username": username})
    if not doc:
        return []
    messages = doc.get("messages", [])
    return messages[-limit:]


def clear_history(username: str) -> None:
    db = get_db()
    db["chats"].update_one(
        {"username": username},
        {"$set": {"messages": []}},
        upsert=True,
    )


def get_session_messages(username: str) -> list[dict]:
    """
    Returns messages formatted for the LLM context window
    (role + content only, no timestamps).
    """
    raw = get_history(username, limit=30)
    return [{"role": m["role"], "content": m["content"]} for m in raw]
