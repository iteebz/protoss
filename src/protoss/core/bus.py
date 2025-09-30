"""Simple message bus for conversational coordination."""

import asyncio
import time
from typing import Dict, List, Optional

from .protocols import Message, Storage
from ..lib.storage import default_storage


class Bus:
    """Minimal message bus - stores and routes conversation via a persistent backend."""

    def __init__(self, storage: Storage = None, base_dir: str = None):
        self.storage = storage or default_storage(base_dir=base_dir)
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}

    async def send(self, sender: str, content: str, channel: str = "human"):
        """Send a message to channel and persist it."""
        timestamp = time.time()
        await self.storage.save_message(
            channel=channel, sender=sender, content=content, timestamp=timestamp
        )

        # Notify subscribers in real-time
        message = Message(
            sender=sender, content=content, timestamp=timestamp, channel=channel
        )
        for queue in self.subscribers.get(channel, []):
            await queue.put(message)

    async def get_history(
        self, channel: str = "human", since: Optional[float] = None
    ) -> List[Dict]:
        """Get conversation history from storage."""
        return await self.storage.load_messages(channel=channel, since=since)

    async def subscribe(self, channel: str = "human"):
        """Subscribe to new messages in channel."""
        queue = asyncio.Queue()
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(queue)

        try:
            while True:
                message = await queue.get()
                yield message
        finally:
            self.subscribers[channel].remove(queue)
