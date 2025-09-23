"""Protoss - Constitutional AI coordination through emergent agent swarms."""

import asyncio
import logging
import uuid
from typing import Optional

from .bus import Bus
from .khala import Khala

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

        self.bus = None
        self.khala = None
        self._event_queue = asyncio.Queue()
        self._listener_task = None

    async def __aenter__(self) -> "Protoss":
        """Infrastructure genesis."""
        self.bus = Bus(port=self.port)
        await self.bus.start()
        await asyncio.sleep(0.1)  # Brief moment for Bus initialization

        self.khala = Khala(bus_url=f"ws://localhost:{self.port}")
        await self.khala.connect(client_id="protoss_coordinator")

        # Start event listener
        self._listener_task = asyncio.create_task(self._listen_for_events())

        # Seed the vision
        await self.khala.send(
            channel="nexus",
            sender="protoss",
            content=f"{self.vision} @arbiter",
            event_type="vision_seed",
            coordination_id=self.coordination_id,
            event_payload={"vision": self.vision},
        )

        logger.info("Coordination network online")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Infrastructure dissolution."""
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        if self.khala:
            await self.khala.disconnect()
        if self.bus:
            await self.bus.stop()
        logger.info("Coordination complete")

    async def _listen_for_events(self):
        """Background task to listen for coordination events."""
        try:
            while True:
                message = await self.khala.receive()
                if message:
                    # Convert message to event and queue it
                    event = {
                        "type": message.msg_type,
                        "channel": message.channel,
                        "sender": message.sender,
                        "timestamp": message.timestamp,
                        "content": message.event.get("content", "")
                        if message.event
                        else "",
                        "payload": message.event,
                    }
                    await self._event_queue.put(event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in event listener: {e}")

    def __aiter__(self):
        """Allows Protoss to be used as an async iterator."""
        return self

    async def __anext__(self):
        """Yields the next coordination event."""
        try:
            # Wait for events with timeout
            event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)

            # Check for completion
            if event.get("type") == "coordination_complete":
                raise StopAsyncIteration

            return event
        except asyncio.TimeoutError:
            # Check if we've exceeded the coordination timeout
            if hasattr(self, "_start_time"):
                if asyncio.get_event_loop().time() - self._start_time > self.timeout:
                    raise StopAsyncIteration
            else:
                self._start_time = asyncio.get_event_loop().time()
            # Continue waiting for more events
            return await self.__anext__()

    async def completion(self) -> str:
        """Awaits coordination completion and returns result."""
        async for event in self:
            if event.get("type") == "coordination_complete":
                return event.get("payload", {}).get("result", "Coordination completed")
        return "Coordination timeout"

    def __await__(self):
        """Allow 'await swarm' syntax."""
        return self.completion().__await__()
