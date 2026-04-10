"""
database/users.py
User authentication and preference management.
"""

from __future__ import annotations
import hashlib
import os
from datetime import datetime
from database.connection import get_db


# ── helpers ────────────────────────────────────────────────────────────────
def _hash_pw(password: str) -> str:
    """SHA-256 hash (bcrypt preferred in prod; kept simple for portability)."""
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    except ImportError:
        return hashlib.sha256(password.encode()).hexdigest()


def _check_pw(password: str, hashed: str) -> bool:
    try:
        import bcrypt
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ImportError:
        return hashlib.sha256(password.encode()).hexdigest() == hashed


# ── public API ─────────────────────────────────────────────────────────────
def create_user(username: str, password: str, email: str = "") -> dict | None:
    """
    Register a new user.
    Returns the user doc on success, None if username already taken.
    """
    db = get_db()
    col = db["users"]

    if col.find_one({"username": username}):
        return None  # duplicate

    user = {
        "username": username,
        "email": email,
        "password_hash": _hash_pw(password),
        "created_at": datetime.utcnow().isoformat(),
        "preferences": {
            "budget": "medium",          # low | medium | high
            "preferred_destinations": [],
            "travel_style": "leisure",   # leisure | adventure | business
        },
        "total_trips": 0,
    }
    col.insert_one(user)
    user.pop("password_hash", None)
    return user


def authenticate_user(username: str, password: str) -> dict | None:
    """
    Verify credentials.
    Returns sanitised user doc (no hash) or None.
    """
    db = get_db()
    user = db["users"].find_one({"username": username})
    if not user:
        return None
    if not _check_pw(password, user.get("password_hash", "")):
        return None
    user.pop("password_hash", None)
    return user


def get_user(username: str) -> dict | None:
    db = get_db()
    user = db["users"].find_one({"username": username})
    if user:
        user.pop("password_hash", None)
    return user


def update_preferences(username: str, prefs: dict) -> bool:
    """Merge new preferences into the user document."""
    db = get_db()
    db["users"].update_one(
        {"username": username},
        {"$set": {"preferences": prefs}},
    )
    return True


def increment_trip_count(username: str) -> None:
    db = get_db()
    db["users"].update_one({"username": username}, {"$inc": {"total_trips": 1}})
