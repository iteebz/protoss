"""Protoss - Constitutional AI coordination through emergent agent swarms."""

import logging
import uuid
from typing import Optional

from .bus import Bus
from .khala import Khala
from .event import Event

logger = logging.getLogger(__name__)


class Protoss:
    """Constitutional AI coordination through emergent agent swarms."""

    def __init__(
        self,
        vision: str,
        port: int = 8888,
        timeout: int = 30,
        coordination_id: Optional[str] = None,
    ):
        self.vision = vision
        self.port = port
        self.timeout = timeout
        self.coordination_id = coordination_id or str(uuid.uuid4())

        self.bus = Bus(port=self.port)
        self.khala: Optional[Khala] = None
        self._last_completion_event: Optional[Event] = None

    async def __aenter__(self) -> "Protoss":
        """Infrastructure genesis."""
        await self.bus.start()

        self.khala = Khala(bus_url=self.bus.url)
        await self.khala.connect(agent_id="protoss_client")

        content = self.vision
        if "@arbiter" not in content:
            content += " @arbiter"

        # Seed the vision via the Khala
        await self.khala.send(
            {
                "type": "vision_seed",
                "channel": "nexus",
                "sender": "protoss_client",
                "coordination_id": self.coordination_id,
                "content": content,
            }
        )

        logger.info("Coordination network online")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Infrastructure dissolution."""
        if self.khala:
            await self.khala.disconnect()

        await self.bus.stop()

        logger.info("Coordination complete")

    async def completion(self) -> Event:
        """Awaits a constitutional completion signal from the Arbiter."""
        async for event in self.khala.listen():
            # The constitutional signal for completion is a message from the arbiter
            # in the nexus channel that is not a spawn request.
            if (
                event.channel == "nexus"
                and event.coordination_id == self.coordination_id
                and event.sender.startswith("arbiter")
                and "@" not in event.content
            ):
                self._last_completion_event = event
                return event
        raise TimeoutError("Coordination timeout")  # pragma: no cover

    def __await__(self):
        """Allow 'await swarm' syntax."""
        return self.completion().__await__()
