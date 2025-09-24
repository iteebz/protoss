import logging
import websockets
from typing import Optional, Dict
import uuid

from ..core.config import Config
from ..core.message import Message, Event
from ..core.protocols import Despawn
from ..core import parser
from ..core.khala import Khala
from .registry import get_unit_data

logger = logging.getLogger(__name__)


class Unit:
    """Base class for all Protoss units, providing shared mechanics and lifecycle management."""

    def __init__(
        self,
        unit_type: str,
        channel: str,
        bus_url: str,
        coordination_id: str,
        config: Config = None,
    ):
        self.unit_type = unit_type
        self.channel = channel
        self.coordination_id = coordination_id
        runtime_bus_url = bus_url or (config.bus_url if config else None)
        if config is None:
            self.config = Config(bus_url=runtime_bus_url or Config().bus_url)
        else:
            self.config = config
        self.bus_url = runtime_bus_url or self.config.bus_url
        self.khala: Optional[Khala] = None
        self._running = True
        self.unit_id = f"{unit_type}-{uuid.uuid4().hex[:6]}"
        self.identity_index = 0
        self._load_identity()

    def _load_identity(self):
        """Load unit configuration from registry."""
        self.registry_data = get_unit_data(self.unit_type)  # Updated function call
        if not self.registry_data:
            raise ValueError(f"Unknown unit type: {self.unit_type}")

    async def _connect_websocket(self):
        """Establishes a connection to the Bus using the Khala."""
        if (
            self.khala
            and self.khala._websocket
            and self.khala._websocket.state == websockets.protocol.State.OPEN
        ):
            return
        try:
            self.khala = Khala(bus_url=self.bus_url)
            await self.khala.connect(unit_id=f"unit/{self.unit_id}")
            logger.info(f"{self.unit_id} connected to Bus at {self.bus_url}")
        except Exception as e:
            logger.error(f"{self.unit_id} failed to connect to Bus: {e}")
            self.khala = None

    def _message_to_event(self, message: Message) -> Event:
        """Converts a Khala Message object to a canonical Event object."""
        return Event(
            type=message.msg_type,
            channel=message.channel,
            sender=message.sender,
            timestamp=message.timestamp,
            payload=message.event or {},
            coordination_id=message.coordination_id,
            content=message.event.get("content", "") if message.event else "",
            signals=message.signals,
        )

    async def send_message(
        self,
        content: str,
        event_type: str,
        event_payload: Dict = None,
        coordination_id: Optional[str] = None,
    ):
        """Sends a message to the Khala."""
        if not self.khala or not (
            self.khala._websocket
            and self.khala._websocket.state == websockets.protocol.State.OPEN
        ):
            logger.warning(f"{self.unit_id} khala not open, cannot send message.")
            return

        event = {
            "type": event_type,
            "channel": self.channel,
            "sender": self.unit_id,
            "coordination_id": coordination_id or self.coordination_id,
            "content": content,
            "payload": event_payload or {},
            "signals": [s.to_dict() for s in parser.signals(content)],
        }

        try:
            await self.khala.send(event)
        except Exception as e:
            logger.error(f"Error sending message via Khala: {e}")

    def _should_despawn(self, content: str) -> bool:
        """Check if unit output contains !despawn signal."""
        signals = parser.signals(content)
        return any(isinstance(signal, Despawn) for signal in signals)

    async def recv_message(self, timeout: int = 1) -> Optional[Event]:
        """Receive a message from the Bus and convert it to a canonical Event."""
        if not self.khala:
            return None

        message = await self.khala.receive(timeout=timeout)
        if not message:
            return None
        return self._message_to_event(message)

    async def run(self):
        """Main loop for the unit, handling common setup/teardown."""
        logger.info(f"Unit {self.unit_id} ({self.unit_type}) online in {self.channel}")
        await self._connect_websocket()

        # Emit unit_spawn event
        await self.send_message(
            content=f"Unit {self.unit_id} ({self.unit_type}) spawned.",
            event_type="unit_spawn",
            event_payload={"unit_id": self.unit_id, "unit_type": self.unit_type},
        )

        try:
            # Delegate to subclass implementation
            await self.execute()
        finally:
            logger.info(f"Unit {self.unit_id} ({self.unit_type}) offline.")
            # Emit unit_despawn event before disconnecting
            await self.send_message(
                content=f"Unit {self.unit_id} ({self.unit_type}) despawned.",
                event_type="unit_despawn",
                event_payload={
                    "unit_id": self.unit_id,
                    "unit_type": self.unit_type,
                },
            )
            await self.khala.disconnect()

    async def execute(self):
        """Unit-specific execution behavior. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement execute()")
