"""Cathedral interface for constitutional AI coordination."""

import asyncio
import logging
from typing import Optional

from .bus import Bus
from .khala import Khala
from .message import Message
from .protocols import BaseSignal

logger = logging.getLogger(__name__)


class Protoss:
    """Cathedral interface: async with Protoss(vision) as swarm: result = await swarm"""

    def __init__(
        self,
        vision: str,
        port: int = 8888,
        timeout: int = 3600,
        debug: bool = False,
        max_agents: int = 100,
    ):
        self.vision = vision
        self.port = port
        self.timeout = timeout
        self.debug = debug
        self.max_agents = max_agents

        # Single coordination nucleus (server)
        self.bus = Bus(port=self.port, max_agents=self.max_agents)
        # Khala for Protoss to interact with its own Bus
        self.khala: Optional[Khala] = None
        self.result: Optional[str] = None

    async def __aenter__(self) -> "Protoss":
        """Constitutional infrastructure genesis."""
        await self.bus.start()
        # Initialize and connect the khala for Protoss to interact with its own Bus
        self.khala = Khala(bus_url=f"ws://localhost:{self.port}")
        await self.khala.connect(client_id="protoss_orchestrator")
        logger.info("Constitutional coordination network online")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Constitutional infrastructure dissolution."""
        if self.khala:
            await self.khala.disconnect()
        await self.bus.stop()
        logger.info("Constitutional coordination complete")

    def __await__(self):  # Not async def
        """Constitutional emergence - await for completion."""
        # Seed initial vision with @arbiter mention
        vision_with_arbiter = f"{self.vision} @arbiter"

        # Use the khala to send the initial vision message
        if self.khala:
            asyncio.create_task(
                self.khala.send(
                    content=vision_with_arbiter,
                    channel="nexus",
                    sender="human",
                    msg_type="event",
                )
            )
        else:
            logger.error("Khala not initialized in __await__.")

        # Wait for constitutional completion
        return self._await_completion().__await__()

    async def _await_completion(self) -> str:
        """Monitor nexus channel for completion signals."""
        start_time = asyncio.get_event_loop().time()

        while True:
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > self.timeout:
                return (
                    "Constitutional coordination timeout - agents may still be working"
                )

            if not self.khala:
                logger.error("Khala not initialized in _await_completion.")
                await asyncio.sleep(1)
                continue

            # Get recent messages from nexus channel
            messages_dicts = await self.khala.request_history("nexus")
            messages = [
                Message(
                    sender=m["sender"],
                    channel=m["channel"],
                    timestamp=m["timestamp"],
                    signals=[
                        BaseSignal.deserialize(s)
                        for s in m.get("signals", [])
                        if BaseSignal.deserialize(s)
                    ],
                    event=m.get("event"),
                    msg_type=m.get("msg_type", "event"),
                )
                for m in messages_dicts
            ]

            # Look for completion from arbiter
            for message in reversed(messages[-10:]):  # Check last 10 messages
                if (
                    message.sender.startswith("arbiter")
                    and message.event
                    and any(
                        content in message.event.get("content", "").lower()
                        for content in ["complete", "done", "finished", "!despawn"]
                    )
                ):
                    return message.event.get(
                        "content", "Constitutional mission accomplished"
                    )

            await asyncio.sleep(1)  # Constitutional patience
