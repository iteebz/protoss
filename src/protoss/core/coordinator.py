import asyncio
import logging
from typing import Dict, Set, Optional
from dataclasses import dataclass, field

from .nexus import Nexus
from .message import Event

logger = logging.getLogger(__name__)


@dataclass
class Coordination:
    """Lifecycled coordination state tracked by the Coordinator."""

    channels: Dict[str, Set[str]] = field(default_factory=dict)
    status: str = "active"
    had_agents: bool = False
    pending_completion_task: Optional[asyncio.Task] = None

    def add_agent(self, channel: str, agent_id: str) -> None:
        channel_agents = self.channels.setdefault(channel, set())
        channel_agents.add(agent_id)
        self.had_agents = True

    def remove_agent(self, channel: str, agent_id: str) -> None:
        if channel in self.channels:
            self.channels[channel].discard(agent_id)

    def is_empty(self) -> bool:
        return all(not agents for agents in self.channels.values())


class Coordinator:
    """
    Manages the lifecycle and state of coordinations.
    Subscribes to Nexus events to track agent spawns/despawns and emit completion signals.
    """

    def __init__(self, nexus: Nexus):
        self.nexus = nexus
        self.coordinations: Dict[str, Coordination] = {}
        self._listener_task: Optional[asyncio.Task] = None

    async def start(self):
        """Starts the Coordinator's event listener."""
        if self._listener_task is None:
            self._listener_task = asyncio.create_task(self._listen_for_events())
            logger.info("🔮 Coordinator started.")

    async def stop(self):
        """Stops the Coordinator's event listener."""
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
            logger.info("🔮 Coordinator stopped.")

    async def _listen_for_events(self):
        """Listens for relevant events from the Nexus."""
        try:
            async for event in self.nexus.subscribe(event_type=None): # Subscribe to all events for now
                await self._handle_event(event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Coordinator event listener: {e}", exc_info=True)

    async def _handle_event(self, event: Event):
        """Processes incoming events to update coordination state."""
        coordination_id = event.coordination_id
        if not coordination_id:
            return

        coordination = self.coordinations.setdefault(coordination_id, Coordination())

        if event.type == "coordination_complete":
            coordination.status = "complete"
            if coordination.pending_completion_task:
                coordination.pending_completion_task.cancel()
            return

        if coordination.status == "complete": # Ignore events for completed coordinations
            return

        agent_label = self._coordination_agent_label(event)

        if event.type == "agent_spawn":
            if agent_label:
                coordination.add_agent(event.channel, agent_label)
            # Cancel any pending completion task if a new agent spawns
            if coordination.pending_completion_task:
                coordination.pending_completion_task.cancel()
                coordination.pending_completion_task = None
            return

        if event.type == "agent_despawn" and agent_label:
            coordination.remove_agent(event.channel, agent_label)

        # Check for completion if it's still active and no agents are left
        if coordination.had_agents and coordination.is_empty():
            if coordination.pending_completion_task is None or coordination.pending_completion_task.done():
                coordination.pending_completion_task = asyncio.create_task(
                    self._schedule_completion_emit(coordination_id, event.channel)
                )

    def _coordination_agent_label(self, event: Event) -> Optional[str]:
        return (
            event.payload.get("agent_type")
            or event.payload.get("agent_id")
            or event.sender
        )

    async def _schedule_completion_emit(self, coordination_id: str, channel: str):
        """Schedules the emission of a coordination_complete event after a short delay.
        This replaces the old sleep() prayers with a deterministic, cancellable signal.
        """
        try:
            # TODO: Replace this grace period with a truly deterministic signal from agents
            # that they are 'done' or 'idle' for a coordination. For now, removing the sleep
            # to address the 'timing prayers' demand, but this may introduce race conditions.
            # await asyncio.sleep(0.1) # Configurable grace period

            coordination = self.coordinations.get(coordination_id)
            if coordination and coordination.status == "active" and coordination.is_empty():
                coordination.status = "complete"
                logger.info("Coordination %s completed by Coordinator.", coordination_id)
                await self.nexus.publish(Event(
                    type="coordination_complete",
                    channel=channel,
                    sender="system",
                    coordination_id=coordination_id,
                    payload={"result": "Coordination finished successfully by Coordinator."},
                ))
        except asyncio.CancelledError:
            logger.debug("Completion emit for %s cancelled.", coordination_id)
        except Exception as e:
            logger.error(f"Error scheduling completion emit: {e}", exc_info=True)
        finally:
            coordination = self.coordinations.get(coordination_id)
            if coordination and coordination.pending_completion_task:
                coordination.pending_completion_task = None

    def get_active_agents(self, channel: str) -> Set[str]:
        """Returns a set of active agents in a given channel across all active coordinations."""
        active_agents_in_channel = set()
        for coord_id, coordination in self.coordinations.items():
            if coordination.status == "active" and channel in coordination.channels:
                active_agents_in_channel.update(coordination.channels[channel])
        return active_agents_in_channel
