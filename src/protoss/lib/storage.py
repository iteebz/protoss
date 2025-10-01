"""SQLite storage for the conversation ledger."""

import sqlite3
import time
from pathlib import Path

from .paths import Paths


class DB:
    _initialized_paths = set()

    @classmethod
    def connect(cls, base_dir: str = None):
        """Get database connection with schema initialization."""
        db_path = Paths.db(base_dir=base_dir)

        if str(db_path) not in cls._initialized_paths:
            cls._init_schema(db_path)
            cls._initialized_paths.add(str(db_path))

        return sqlite3.connect(db_path)

    @classmethod
    def _init_schema(cls, db_path: Path):
        """Initialize database schema for the ledger."""
        with sqlite3.connect(db_path) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS ledger (
                    channel TEXT NOT NULL,
                    parent TEXT,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    PRIMARY KEY (channel, timestamp)
                );

                CREATE INDEX IF NOT EXISTS idx_ledger_channel ON ledger(channel);
                CREATE INDEX IF NOT EXISTS idx_ledger_parent ON ledger(parent);
            """)


class SQLite:
    """SQLite storage implementation for the conversation ledger."""

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir

    async def save_message(
        self,
        channel: str,
        sender: str,
        content: str,
        timestamp: float = None,
        parent: str = None,
    ) -> None:
        """Save message to the ledger."""
        import asyncio

        if timestamp is None:
            timestamp = time.time()

        def _sync_save():
            with DB.connect(self.base_dir) as db:
                db.execute(
                    "INSERT INTO ledger (channel, sender, content, timestamp, parent) VALUES (?, ?, ?, ?, ?)",
                    (channel, sender, content, timestamp, parent),
                )

        await asyncio.get_event_loop().run_in_executor(None, _sync_save)

    async def load_messages(
        self, channel: str, since: float | None = None
    ) -> list[dict]:
        """Load messages from the ledger."""
        import asyncio

        def _sync_load():
            with DB.connect(self.base_dir) as db:
                db.row_factory = sqlite3.Row

                query = "SELECT sender, content, timestamp, channel FROM ledger WHERE channel = ?"
                params = [channel]

                if since:
                    query += " AND timestamp > ?"
                    params.append(since)

                query += " ORDER BY timestamp"

                rows = db.execute(query, params).fetchall()
                return [dict(row) for row in rows]

        return await asyncio.get_event_loop().run_in_executor(None, _sync_load)

    async def get_channels(self) -> list[str]:
        """Get list of active channels."""
        import asyncio

        def _sync_get():
            with DB.connect(self.base_dir) as db:
                rows = db.execute(
                    "SELECT DISTINCT channel FROM ledger ORDER BY channel"
                ).fetchall()
                return [row[0] for row in rows]

        return await asyncio.get_event_loop().run_in_executor(None, _sync_get)

    async def get_parent_channel(self, channel: str) -> str | None:
        """Get parent channel for a given channel."""
        import asyncio

        def _sync_get():
            with DB.connect(self.base_dir) as db:
                row = db.execute(
                    "SELECT parent FROM ledger WHERE channel = ? AND parent IS NOT NULL LIMIT 1",
                    (channel,),
                ).fetchone()
                return row[0] if row else None

        return await asyncio.get_event_loop().run_in_executor(None, _sync_get)


def default_storage(base_dir: str | None = None):
    return SQLite(base_dir=base_dir)
