import logging
import asyncio
from typing import Optional

from ..core.config import Config
from ..core.message import Event
from .unit import Unit

logger = logging.getLogger(__name__)


class Probe(Unit):
    """Mechanistic agent that executes specific commands."""

    def __init__(
        self,
        unit_type: str,
        channel: str,
        bus_url: str,
        coordination_id: str,
        config: Optional[Config] = None,
    ):
        super().__init__(unit_type, channel, bus_url, coordination_id, config)

    def _load_identity(self):
        """Load unit configuration from registry - Probe override."""
        # Probe units don't use LLM identity/tools from registry
        self.registry_data = {"identity": [], "guidelines": [], "tools": []}

    async def execute(self):
        """Execute mechanistic function behavior."""
        while self._running:
            try:
                event = await self.recv_message()
                if event:
                    await self._handle_probe_command(event)
            except asyncio.CancelledError:
                logger.info(f"Probe Agent {self.unit_id} cancelled.")
                self._running = False
            except Exception as e:
                logger.error(f"Probe Agent {self.unit_id} error: {e}")

    async def _handle_probe_command(self, event: Event):
        """Handle probe commands from event."""
        # TODO: Implement probe command handling
        logger.info(f"Probe {self.unit_id} handling command: {event.content}")
