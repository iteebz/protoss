from pathlib import Path
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import os

DB = Path(os.getcwd()) / ".protoss" / "store.db"

@dataclass
class Run:
    id: str
    task: str
    agents: str
    channel: str
    started_at: str
    completed_at: str | None
    message_count: int
    outcome: str | None


@contextmanager
def get_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                task TEXT NOT NULL,
                agents TEXT NOT NULL,
                channel TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                message_count INTEGER DEFAULT 0,
                outcome TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_started ON runs(started_at DESC)
        """)
        conn.commit()


def start(run_id: str, task: str, agents: list[str], channel: str) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO runs (id, task, agents, channel, started_at) VALUES (?, ?, ?, ?, ?)",
            (run_id, task, ",".join(agents), channel, datetime.utcnow().isoformat())
        )
        conn.commit()


def complete(run_id: str, outcome: str, msg_count: int) -> None:
    with get_db() as conn:
        conn.execute(
            """UPDATE runs 
               SET completed_at=?, outcome=?, message_count=? 
               WHERE id=?""",
            (datetime.utcnow().isoformat(), outcome, msg_count, run_id)
        )
        conn.commit()


def list_runs(limit: int = 10) -> list[Run]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [Run(**dict(r)) for r in rows]
