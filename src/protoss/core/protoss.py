"""Protoss - Constitutional AI coordination through emergent agent swarms."""

import logging
import uuid
from typing import Optional

from .bus import Bus
from .khala import Khala
from .nexus import Nexus
from .coordinator import Coordinator
from .archiver import Archiver
from .observer import Observer
from .message import Event  # Import Event dataclass
from . import gateway

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

        # New Architecture Components
        self.nexus = Nexus()
        self.bus = Bus(nexus=self.nexus, port=self.port)
        self.coordinator = Coordinator(nexus=self.nexus)
        self.archiver = Archiver(nexus=self.nexus)
        self.observer = Observer(
            nexus=self.nexus,
            coordinator=self.coordinator,
            bus_url=self.bus.url,
            spawn_unit_func=gateway.spawn_unit,
        )

        # Old components (will be removed or refactored)
        self.khala = None  # Khala will connect to Bus
        self._last_completion_event: Optional[Event] = None

    async def __aenter__(self) -> "Protoss":
        """Infrastructure genesis."""
        await self.bus.start()
        await self.coordinator.start()
        await self.archiver.start()
        await self.observer.start()

        self.khala = Khala(bus_url=self.bus.url)
        await self.khala.connect(unit_id="protoss_coordinator")

        # Seed the vision via Nexus
        vision_event = Event(
            type="vision_seed",
            channel="nexus",
            sender="protoss",
            coordination_id=self.coordination_id,
            payload={"vision": self.vision},
            content=f"{self.vision} @arbiter",
        )
        await self.nexus.publish(vision_event)

        logger.info("Coordination network online")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Infrastructure dissolution."""
        if self.khala:
            await self.khala.disconnect()

        await self.observer.stop()
        await self.archiver.stop()
        await self.coordinator.stop()
        await self.bus.stop()

        logger.info("Coordination complete")

    # The Protoss class no longer directly listens for events or manages an event queue.
    # Completion is now handled by subscribing to the Coordinator's completion events.

    async def completion(self) -> str:
        """Awaits coordination completion and returns result."""
        async for event in self.nexus.subscribe(
            event_type="coordination_complete", channel="nexus"
        ):
            if event.coordination_id == self.coordination_id:
                self._last_completion_event = event
                return event.payload.get("result", "Coordination completed")
        return "Coordination timeout"

    def __await__(self):
        """Allow 'await swarm' syntax."""
        return self.completion().__await__()
