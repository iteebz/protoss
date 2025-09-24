import asyncio
import logging
from typing import Optional, List, Dict # Added List, Dict

from .nexus import Nexus
from .message import Event
from protoss.lib.storage import SQLite
from .protocols import Storage

logger = logging.getLogger(__name__)


class Archiver:
    """
    Persists all events flowing through the Nexus to durable storage.
    Handles history requests.
    """

    def __init__(self, nexus: Nexus, storage_path: Optional[str] = None):
        self.nexus = nexus
        self.storage: Storage = SQLite(storage_path or "./.protoss/store.db")
        self._listener_task: Optional[asyncio.Task] = None

    async def start(self):
        """Starts the Archiver's event listener."""
        if self._listener_task is None:
            self._listener_task = asyncio.create_task(self._listen_for_events())
            logger.info("🔮 Archiver started.")

    async def stop(self):
        """Stops the Archiver's event listener."""
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
            logger.info("🔮 Archiver stopped.")

    async def _listen_for_events(self):
        """Listens for all events from the Nexus and persists them."""
        try:
            async for event in self.nexus.subscribe(event_type=None): # Subscribe to all events
                await self._persist_event(event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Archiver event listener: {e}", exc_info=True)

    async def _persist_event(self, event: Event) -> None:
        """Persist the event, logging any failure."""
        try:
            await self.storage.save_event(event.to_dict())
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("❌ Failed to save event: %s", exc, exc_info=True)

    async def get_events(
        self, channel: str, since: Optional[float] = None
    ) -> List[Dict]:
        """Retrieves events from storage for a given channel."""
        return await self.storage.load_events(channel=channel, since=since)
