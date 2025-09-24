import asyncio
import logging
from typing import Optional, Callable  # Added Callable

from .nexus import Nexus
from .message import Event
from .protocols import Mention
from . import gateway
from .coordinator import Coordinator  # Import Coordinator

logger = logging.getLogger(__name__)


class Observer:
    """
    Watches for @mentions in unit messages and triggers unit spawning via the Gateway.
    """

    def __init__(
        self,
        nexus: Nexus,
        coordinator: Coordinator,
        bus_url: str,
        spawn_unit_func: Callable,
        max_units: int = 100,
    ):
        self.nexus = nexus
        self.coordinator = coordinator  # Store Coordinator instance
        self.bus_url = bus_url
        self.spawn_unit_func = spawn_unit_func  # Store spawn_unit_func
        self.max_units = (
            max_units  # Max units per channel, passed to gateway.should_spawn_unit
        )
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
                await self._handle_unit_message(event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Observer event listener: {e}", exc_info=True)

    async def _handle_unit_message(self, event: Event):
        """Processes unit_message events to detect @mentions and trigger spawns."""
        if not event.signals:
            return

        for signal in event.signals:
            if not isinstance(signal, Mention):
                continue

            unit_type = signal.agent_name  # Renamed to unit_type
            channel = event.channel

            # Query Coordinator for active units
            active_units_in_channel = self.coordinator.get_active_units(channel)
            active_units_snapshot = {channel: set(active_units_in_channel)}

            if not gateway.should_spawn_unit(
                unit_type, channel, active_units_snapshot, self.max_units
            ):
                continue

            await self._spawn_unit_and_publish_event(unit_type, channel, event)

    async def _spawn_unit_and_publish_event(
        self, unit_type: str, channel: str, original_event: Event
    ):
        """Spawns a unit and publishes an unit_spawn event to the Nexus."""
        try:
            spawn_coro = self.spawn_unit_func(
                unit_type, channel, self.bus_url
            )  # Use spawn_unit_func
            await spawn_coro
            logger.info("Observer: Spawning %s for @mention in %s", unit_type, channel)

            # Publish unit_spawn event to Nexus
            await self.nexus.publish(
                Event(
                    type="unit_spawn",  # Renamed event type
                    channel=channel,
                    sender="system",
                    coordination_id=original_event.coordination_id,
                    payload={
                        "unit_type": unit_type,
                        "spawned_by": original_event.sender,
                    },
                )
            )
        except Exception as exc:
            logger.error(
                "Observer: Failed to spawn %s: %s", unit_type, exc, exc_info=True
            )
