import aiosqlite
import asyncio
import json
import os
import time  # Added time import
from typing import List, Dict, Optional

from ..core.protocols import Storage


class SQLite(Storage):
    """SQLite-based storage for Bus events, adhering to the Storage protocol."""

    def __init__(self, db_path: str = "./.protoss/store.db"):
        self.db_path = db_path
        self._init_lock = asyncio.Lock()

    async def _init_db(self):
        # Ensure the directory for the database exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with self._init_lock:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL,
                        coordination_id TEXT,
                        channel TEXT NOT NULL,
                        sender TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        event_json TEXT NOT NULL
                    )
                    """
                )
                await db.commit()

    async def save_event(self, event: Dict) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            event_json = json.dumps(event)
            await db.execute(
                "INSERT INTO events (type, coordination_id, channel, sender, timestamp, event_json) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event.get("type", "unknown"),
                    event.get("coordination_id"),
                    event.get("channel", "general"),
                    event.get("sender", "system"),
                    event.get("timestamp", time.time()),
                    event_json,
                ),
            )
            await db.commit()

    async def load_events(
        self, channel: str, since: Optional[float] = None, limit: Optional[int] = None
    ) -> List[Dict]:
        """Load all events for a specific channel, ordered chronologically."""
        await self._init_db()
        events = []
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT event_json FROM events WHERE channel = ?"
            params = [channel]

            if since is not None:
                query += " AND timestamp > ?"
                params.append(since)

            query += " ORDER BY timestamp ASC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            async with db.execute(query, params) as cursor:
                async for row in cursor:
                    events.append(json.loads(row[0]))
        return events

    async def load_coordinations(self) -> List[Dict]:
        await self._init_db()
        coordinations_data = []
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT coordination_id, MIN(timestamp), MAX(timestamp), COUNT(*) FROM events WHERE coordination_id IS NOT NULL GROUP BY coordination_id"
            async with db.execute(query) as cursor:
                async for row in cursor:
                    coordination_id, created_at, last_active, event_count = row
                    coordinations_data.append(
                        {
                            "id": coordination_id,
                            "created_at": created_at,
                            "last_active": last_active,
                            "event_count": event_count,
                        }
                    )
        return coordinations_data

    async def recent_events(self, channel: str, limit: int = 10) -> List[Dict]:
        await self._init_db()
        recent_events_data = []
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT event_json FROM events WHERE channel = ? ORDER BY timestamp DESC LIMIT ?"
            async with db.execute(query, (channel, limit)) as cursor:
                async for row in cursor:
                    recent_events_data.append(json.loads(row[0]))
        return list(reversed(recent_events_data))  # Return in chronological order
