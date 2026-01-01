"""Simple persistent memory for Jarvis.

Stores messages (user and assistant) in a SQLite database under jarvis_data/
Provides helpers to save conversations, recall recent history, search, summarize,
and prune old entries according to retention policy.

This is lightweight and self-contained (no external services).
"""
from __future__ import annotations
import sqlite3
import os
import json
import time
from typing import List, Dict, Optional

DB_FILENAME = 'jarvis_memory.db'
DEFAULT_RETENTION_DAYS: Optional[int] = None  # None == keep forever


def _db_path() -> str:
    d = os.path.join(os.getcwd(), 'jarvis_data')
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, DB_FILENAME)


def _data_dir_path() -> str:
    """Return the project-level `data/` folder path (user requested).

    This is separate from `jarvis_data/` and will contain a human-readable
    JSONL memory file so the user can open it easily.
    """
    d = os.path.join(os.getcwd(), 'data')
    os.makedirs(d, exist_ok=True)
    return d


def _memory_jsonl_path() -> str:
    return os.path.join(_data_dir_path(), 'memory.jsonl')


def _connect():
    path = _db_path()
    conn = sqlite3.connect(path, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp REAL NOT NULL,
            metadata TEXT
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
    conn.commit()
    conn.close()


# Initialize on import
init_db()


def save_message(sender: str, text: str, metadata: Optional[Dict] = None, ts: Optional[float] = None) -> int:
    """Save a single message. Returns the inserted row id."""
    if ts is None:
        ts = time.time()
    meta_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
    conn = _connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (sender, text, timestamp, metadata) VALUES (?, ?, ?, ?)",
                (sender, text, ts, meta_json))
    rid = cur.lastrowid
    conn.commit()
    conn.close()
    # Also append a human-readable JSONL entry to data/memory.jsonl so the
    # conversation is visible and portable outside the sqlite DB.
    try:
        mem_path = _memory_jsonl_path()
        entry = {'id': rid, 'sender': sender, 'text': text, 'timestamp': ts, 'metadata': metadata}
        with open(mem_path, 'a', encoding='utf-8') as jf:
            jf.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        # best-effort: do not fail the DB write
        pass
    return rid


def save_conversation(user_text: str, assistant_text: str, metadata: Optional[Dict] = None) -> None:
    """Save a pair of messages (user then assistant)."""
    save_message('user', user_text, metadata)
    save_message('assistant', assistant_text, metadata)


def recall_last(n: int = 10) -> List[Dict]:
    """Return the last n messages as a list of dicts ordered newest->oldest."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT id, sender, text, timestamp, metadata FROM messages ORDER BY timestamp DESC LIMIT ?", (n,))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        meta = None
        try:
            meta = json.loads(r[4]) if r[4] else None
        except Exception:
            meta = None
        out.append({'id': r[0], 'sender': r[1], 'text': r[2], 'timestamp': r[3], 'metadata': meta})
    return out


def search_history(query: str, limit: int = 10) -> List[Dict]:
    """Simple substring search over messages (case-insensitive)."""
    q = f"%{query}%"
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT id, sender, text, timestamp, metadata FROM messages WHERE text LIKE ? ORDER BY timestamp DESC LIMIT ?", (q, limit))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        meta = None
        try:
            meta = json.loads(r[4]) if r[4] else None
        except Exception:
            meta = None
        out.append({'id': r[0], 'sender': r[1], 'text': r[2], 'timestamp': r[3], 'metadata': meta})
    return out


def summarize_recent(n: int = 10) -> str:
    """Return a naive concatenation summary of the last n messages.

    This is a simple helper; for real summarization you can replace this with
    an LLM call.
    """
    msgs = recall_last(n)
    parts = []
    # oldest first for readability
    for m in reversed(msgs):
        sender = 'You' if m['sender'] == 'user' else 'Jarvis'
        ts = time.strftime('%Y-%m-%d %H:%M', time.localtime(m['timestamp']))
        parts.append(f"[{ts}] {sender}: {m['text']}")
    return "\n".join(parts)


def prune_old(retention_days: Optional[int] = DEFAULT_RETENTION_DAYS) -> int:
    """Delete messages older than retention_days. Returns number of rows deleted.

    If retention_days is None, nothing is deleted.
    """
    if retention_days is None:
        return 0
    cutoff = time.time() - float(retention_days) * 86400.0
    conn = _connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM messages WHERE timestamp < ?", (cutoff,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted


def set_retention_days(days: Optional[int]):
    """Convenience wrapper: prune immediately and future calls should call prune_old periodically."""
    return prune_old(days)
