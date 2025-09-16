"""SQLite storage with ACID properties for Khala pathway persistence."""

import sqlite3
import time
from pathlib import Path

from .paths import Paths
from .protocols import Storage


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
        """Initialize Khala persistence schema."""
        with sqlite3.connect(db_path) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS pathways (
                    name TEXT PRIMARY KEY,
                    created_at REAL NOT NULL,
                    last_active REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS psi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pathway TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (pathway) REFERENCES pathways(name)
                );

                CREATE INDEX IF NOT EXISTS idx_psi_pathway ON psi(pathway);
                CREATE INDEX IF NOT EXISTS idx_psi_timestamp ON psi(timestamp);
                CREATE INDEX IF NOT EXISTS idx_psi_pathway_time ON psi(pathway, timestamp);
                CREATE INDEX IF NOT EXISTS idx_pathways_activity ON pathways(last_active DESC);
            """)


class SQLite(Storage):
    """SQLite implementation of Storage protocol for Khala pathway persistence."""

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir

    async def save_psi(self, pathway: str, sender: str, content: str, timestamp: float = None) -> None:
        """Save psi transmission to pathway with retry logic."""
        import asyncio

        if timestamp is None:
            timestamp = time.time()

        def _sync_save():
            with DB.connect(self.base_dir) as db:
                # Ensure pathway exists
                db.execute(
                    "INSERT OR IGNORE INTO pathways (name, created_at, last_active) VALUES (?, ?, ?)",
                    (pathway, timestamp, timestamp),
                )
                # Update last_active
                db.execute(
                    "UPDATE pathways SET last_active = ? WHERE name = ?",
                    (timestamp, pathway),
                )
                # Save psi transmission
                db.execute(
                    "INSERT INTO psi (pathway, sender, content, timestamp) VALUES (?, ?, ?, ?)",
                    (pathway, sender, content, timestamp),
                )

        await asyncio.get_event_loop().run_in_executor(None, _sync_save)

    async def load_pathway_psi(self, pathway: str, since: float = 0, limit: int = None) -> list[dict]:
        """Load psi transmissions from pathway since timestamp."""
        import asyncio

        def _sync_load():
            with DB.connect(self.base_dir) as db:
                db.row_factory = sqlite3.Row

                query = "SELECT sender, content, timestamp FROM psi WHERE pathway = ? AND timestamp > ? ORDER BY timestamp"
                params = [pathway, since]

                if limit is not None:
                    query += " LIMIT ?"
                    params.append(limit)

                rows = db.execute(query, params).fetchall()
                return [{"sender": row["sender"], "content": row["content"], "timestamp": row["timestamp"]} for row in rows]

        return await asyncio.get_event_loop().run_in_executor(None, _sync_load)

    async def load_pathways(self) -> list[dict]:
        """Load all pathways with activity stats."""
        import asyncio

        def _sync_load():
            with DB.connect(self.base_dir) as db:
                db.row_factory = sqlite3.Row

                query = """
                    SELECT 
                        p.name,
                        p.created_at,
                        p.last_active,
                        COUNT(psi.id) as message_count
                    FROM pathways p
                    LEFT JOIN psi ON p.name = psi.pathway
                    GROUP BY p.name
                    ORDER BY p.last_active DESC
                """

                rows = db.execute(query).fetchall()
                return [
                    {
                        "name": row["name"],
                        "created_at": row["created_at"],
                        "last_active": row["last_active"],
                        "message_count": row["message_count"],
                    }
                    for row in rows
                ]

        return await asyncio.get_event_loop().run_in_executor(None, _sync_load)

    async def get_recent_messages(self, pathway: str, limit: int = 10) -> list[str]:
        """Get recent message content from pathway."""
        psi_data = await self.load_pathway_psi(pathway, limit=limit)
        return [psi["content"] for psi in psi_data[-limit:]]  # Most recent


def default_storage():
    """Get default storage instance."""
    return SQLite()