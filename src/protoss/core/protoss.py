"""Cathedral interface for constitutional AI coordination."""

import asyncio
import logging
from typing import Optional

from .bus import Bus

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

        # Single coordination nucleus
        self.bus = Bus(port=self.port, max_agents=self.max_agents)
        self.result: Optional[str] = None

    async def __aenter__(self) -> "Protoss":
        """Constitutional infrastructure genesis."""
        await self.bus.start()
        logger.info("Constitutional coordination network online")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Constitutional infrastructure dissolution."""
        await self.bus.stop()
        logger.info("Constitutional coordination complete")

    def __await__(self):  # Not async def
        """Constitutional emergence - await for completion."""
        # Seed initial vision with @arbiter mention
        vision_with_arbiter = f"{self.vision} @arbiter"

        # Create message and broadcast to nexus channel
        message_event = {"content": vision_with_arbiter}
        # Await the broadcast, as it's an async operation
        asyncio.create_task(self.bus.transmit("nexus", "human", event=message_event))

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

            # Get recent messages from nexus channel
            messages = self.bus.get_history("nexus")

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
