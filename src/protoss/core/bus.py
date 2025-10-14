"""Simple message bus for conversational coordination."""

import asyncio
import time
from typing import Dict, List, Optional

from .protocols import Message, Storage
from ..lib.sqlite import default_storage
from ..lib.routing import parse_route, format_stub


class Bus:
    """Minimal message bus - stores and routes conversation via a persistent backend."""

    def __init__(self, storage: Storage = None, base_dir: str = None):
        self.storage = storage or default_storage(base_dir=base_dir)
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}

    async def send(self, sender: str, content: str, channel: str = "human"):
        """Send a message to channel and persist it.

        Supports cross-channel routing via #channel: anywhere in message.
        Example: 'After analysis, #main: we should proceed' routes to #main.
        """
        timestamp = time.time()

        # Check for cross-channel routing
        potential_target, message_body = parse_route(content)
        target_channel = channel
        routed_content = content

        if potential_target:
            # Verify target channel exists
            channels = await self.storage.get_channels()
            if potential_target in channels or potential_target == "human":
                target_channel = potential_target
                routed_content = message_body

                # Leave forwarding stub in source channel
                await self.storage.save_message(
                    channel=channel,
                    sender=sender,
                    content=format_stub(target_channel, message_body),
                    timestamp=timestamp,
                )

        # Send to target channel
        await self.storage.save_message(
            channel=target_channel,
            sender=sender,
            content=routed_content,
            timestamp=timestamp,
        )

        # Notify subscribers in real-time
        message = Message(
            sender=sender,
            content=routed_content,
            timestamp=timestamp,
            channel=target_channel,
        )
        for queue in self.subscribers.get(target_channel, []):
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
