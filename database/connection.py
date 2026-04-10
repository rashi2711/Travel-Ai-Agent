"""
database/connection.py
MongoDB connection with caching and graceful fallback to in-memory store.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "travel_ai")

# ── In-memory fallback (used when MongoDB is unavailable) ──────────────────
_mem_db: dict[str, list] = {
    "users": [],
    "chats": [],
    "bookings": [],
}


def _is_mem_mode() -> bool:
    return st.session_state.get("_use_mem_db", False)


# ── Cached real MongoDB client ──────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _get_mongo_client():
    """Return a MongoClient, or None if connection fails."""
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError

        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")          # quick connectivity check
        return client
    except Exception as exc:
        print(f"[DB] MongoDB unavailable ({exc}). Using in-memory fallback.")
        return None


def get_db():
    """
    Return a database-like object.
    • Real MongoDB if reachable.
    • MemDB wrapper otherwise (so callers never crash).
    """
    client = _get_mongo_client()
    if client is not None:
        return client[DB_NAME]

    # Switch session to memory mode once
    if not st.session_state.get("_use_mem_db"):
        st.session_state["_use_mem_db"] = True
    return _MemDB()


# ── Lightweight in-memory database mirroring pymongo's API ─────────────────
class _MemCollection:
    """Mimics a pymongo Collection with basic CRUD."""

    def __init__(self, name: str):
        self.name = name
        self._data = _mem_db.setdefault(name, [])

    # ---- write ----
    def insert_one(self, doc: dict):
        import uuid
        doc = dict(doc)
        doc.setdefault("_id", str(uuid.uuid4()))
        self._data.append(doc)

        class _Result:
            inserted_id = doc["_id"]
        return _Result()

    def insert_many(self, docs):
        for d in docs:
            self.insert_one(d)

    def update_one(self, filt: dict, update: dict, upsert=False):
        for doc in self._data:
            if self._match(doc, filt):
                self._apply(doc, update)
                return
        if upsert:
            new_doc = dict(filt)
            self._apply(new_doc, update)
            self.insert_one(new_doc)

    def delete_one(self, filt: dict):
        for i, doc in enumerate(self._data):
            if self._match(doc, filt):
                self._data.pop(i)
                return

    # ---- read ----
    def find_one(self, filt: dict = None):
        filt = filt or {}
        for doc in self._data:
            if self._match(doc, filt):
                return dict(doc)
        return None

    def find(self, filt: dict = None, sort=None, limit=0):
        filt = filt or {}
        results = [dict(d) for d in self._data if self._match(d, filt)]
        if sort:
            for key, direction in reversed(sort):
                results.sort(key=lambda x: x.get(key, ""), reverse=(direction == -1))
        if limit:
            results = results[:limit]
        return iter(results)

    def count_documents(self, filt: dict = None):
        filt = filt or {}
        return sum(1 for d in self._data if self._match(d, filt))

    def aggregate(self, pipeline):
        """Very limited aggregate — returns all docs (sufficient for seed data)."""
        return iter([dict(d) for d in self._data])

    def create_index(self, *args, **kwargs):
        pass  # no-op

    # ---- helpers ----
    @staticmethod
    def _match(doc: dict, filt: dict) -> bool:
        for k, v in filt.items():
            if isinstance(v, dict):
                # support $gte / $lte / $in
                dv = doc.get(k)
                for op, val in v.items():
                    if op == "$gte" and not (dv >= val):
                        return False
                    if op == "$lte" and not (dv <= val):
                        return False
                    if op == "$in" and dv not in val:
                        return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    @staticmethod
    def _apply(doc: dict, update: dict):
        for op, fields in update.items():
            if op == "$set":
                doc.update(fields)
            elif op == "$push":
                for fk, fv in fields.items():
                    doc.setdefault(fk, []).append(fv)
            elif op == "$inc":
                for fk, fv in fields.items():
                    doc[fk] = doc.get(fk, 0) + fv


class _MemDB:
    def __getitem__(self, name: str) -> _MemCollection:
        return _MemCollection(name)

    def __getattr__(self, name: str) -> _MemCollection:
        return _MemCollection(name)
