import asyncio
import logging
from typing import Optional, Dict, Set

from .nexus import Nexus
from .message import Event
from .protocols import Mention
from . import gateway
from .coordinator import Coordinator # Import Coordinator

logger = logging.getLogger(__name__)


class Observer:
    """
    Watches for @mentions in agent messages and triggers agent spawning via the Gateway.
    """

    def __init__(self, nexus: Nexus, coordinator: Coordinator, bus_url: str, max_agents: int = 100):
        self.nexus = nexus
        self.coordinator = coordinator # Store Coordinator instance
        self.bus_url = bus_url
        self.max_agents = max_agents # Max agents per channel, passed to gateway.should_spawn
        self._listener_task: Optional[asyncio.Task] = None

    async def start(self):
        """Starts the Observer's event listener."""
        if self._listener_task is None:
            self._listener_task = asyncio.create_task(self._listen_for_events())
            logger.info("🔮 Observer started.")

    async def stop(self):
        """Stops the Observer's event listener."""
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
            logger.info("🔮 Observer stopped.")

    async def _listen_for_events(self):
        """Listens for agent_message events from the Nexus."""
        try:
            async for event in self.nexus.subscribe(event_type="agent_message"):
                await self._handle_agent_message(event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Observer event listener: {e}", exc_info=True)

    async def _handle_agent_message(self, event: Event):
        """Processes agent_message events to detect @mentions and trigger spawns."""
        if not event.signals:
            return

        for signal in event.signals:
            if not isinstance(signal, Mention):
                continue

            agent_type = signal.agent_name
            channel = event.channel

            # Query Coordinator for active agents
            active_agents_in_channel = self.coordinator.get_active_agents(channel)

            if not gateway.should_spawn(
                agent_type, channel, active_agents_in_channel, self.max_agents
            ):
                continue

            await self._spawn_agent_and_publish_event(agent_type, channel, event)

    async def _spawn_agent_and_publish_event(self, agent_type: str, channel: str, original_event: Event):
        """Spawns an agent and publishes an agent_spawn event to the Nexus."""
        try:
            spawn_coro = gateway.spawn_agent(agent_type, channel, self.bus_url)
            await spawn_coro
            logger.info("Observer: Spawning %s for @mention in %s", agent_type, channel)

            # Publish agent_spawn event to Nexus
            await self.nexus.publish(Event(
                type="agent_spawn",
                channel=channel,
                sender="system",
                coordination_id=original_event.coordination_id,
                payload={
                    "agent_type": agent_type,
                    "spawned_by": original_event.sender,
                },
            ))
        except Exception as exc:
            logger.error("Observer: Failed to spawn %s: %s", agent_type, exc, exc_info=True)
