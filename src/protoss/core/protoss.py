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

        logger.info("Coordination network online")
        return self

    async def seed_vision(self):
        """Seed the vision into #human for agent self-selection."""
        await self.khala.send(
            {
                "type": "vision_seed",
                "channel": "human",
                "sender": "protoss_client",
                "coordination_id": self.coordination_id,
                "content": self.vision,
            }
        )
        logger.info(f"Vision seeded: {self.vision}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Infrastructure dissolution."""
        if self.khala:
            await self.khala.disconnect()

        await self.bus.stop()

        logger.info("Coordination complete")

    async def completion(self) -> Event:
        """Awaits constitutional completion signal from any claiming agent."""
        # Seed vision after listener is ready
        await self.seed_vision()

        async for event in self.khala.listen():
            logger.info(
                f"Completion check: channel={event.channel}, coord={event.coordination_id}, sender={event.sender}, type={event.type}"
            )
            # Constitutional completion: any agent can !complete
            if (
                event.channel == "human"
                and event.coordination_id == self.coordination_id
                and event.type == "agent_message"
                and "!complete" in event.content
            ):
                logger.info(f"Completion detected: {event.content}")
                self._last_completion_event = event
                return event
        raise TimeoutError("Coordination timeout")  # pragma: no cover

    def __await__(self):
        """Allow 'await swarm' syntax."""
        return self.completion().__await__()
