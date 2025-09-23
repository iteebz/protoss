import aiosqlite
import asyncio
import json
import os
from typing import List, Dict, Optional
from dataclasses import asdict  # Import asdict

from ..core.protocols import Storage
from ..core.message import Message
from ..core.protocols import BaseSignal


class SQLite(Storage):
    """SQLite-based storage for Bus messages, adhering to the Storage protocol."""

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
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channel TEXT NOT NULL,
                        sender TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        event_json TEXT,
                        signals_json TEXT
                    )
                    """
                )
                await db.commit()

    async def save_message(self, message: Message) -> None:
        await self._init_db()
        async with aiosqlite.connect(self.db_path) as db:
            event_json = json.dumps(message.event) if message.event else None
            signals_json = (
                json.dumps([asdict(s) for s in message.signals])
                if message.signals
                else None
            )
            await db.execute(
                "INSERT INTO messages (channel, sender, timestamp, event_json, signals_json) VALUES (?, ?, ?, ?, ?)",
                (
                    message.channel,
                    message.sender,
                    message.timestamp,
                    event_json,
                    signals_json,
                ),
            )
            await db.commit()

    async def load_messages(
        self, channel: str, since: float = 0, limit: Optional[int] = None
    ) -> List[Message]:
        await self._init_db()
        messages = []
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT channel, sender, timestamp, event_json, signals_json FROM messages WHERE channel = ? AND timestamp > ? ORDER BY timestamp ASC"
            params = [channel, since]
            if limit:
                query += " LIMIT ?"
                params.append(limit)

            async with db.execute(query, params) as cursor:
                async for row in cursor:
                    channel_name, sender, timestamp, event_json, signals_json = row
                    event = json.loads(event_json) if event_json else None

                    reconstructed_signals = []
                    if signals_json:
                        s_dicts = json.loads(signals_json)
                        for s_dict in s_dicts:
                            signal = BaseSignal.deserialize(s_dict)
                            if signal:
                                reconstructed_signals.append(signal)

                    messages.append(
                        Message(
                            channel=channel_name,
                            sender=sender,
                            timestamp=timestamp,
                            event=event,
                            signals=reconstructed_signals,
                        )
                    )
        return messages

    async def load_channels(self) -> List[Dict]:
        await self._init_db()
        channels_data = []
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT channel, MIN(timestamp), MAX(timestamp), COUNT(*) FROM messages GROUP BY channel"
            async with db.execute(query) as cursor:
                async for row in cursor:
                    channel_name, created_at, last_active, message_count = row
                    channels_data.append(
                        {
                            "name": channel_name,
                            "created_at": created_at,
                            "last_active": last_active,
                            "message_count": message_count,
                        }
                    )
        return channels_data

    async def recent(self, channel: str, limit: int = 10) -> List[str]:
        await self._init_db()
        recent_contents = []
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT event_json FROM messages WHERE channel = ? AND event_json IS NOT NULL ORDER BY timestamp DESC LIMIT ?"
            async with db.execute(query, (channel, limit)) as cursor:
                async for row in cursor:
                    event = json.loads(row[0])
                    if "content" in event:
                        recent_contents.append(event["content"])
        return list(reversed(recent_contents))  # Return in chronological order
