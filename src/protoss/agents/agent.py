"""Single Constitutional AI Agent - Data-driven from registry."""

import asyncio
import logging
import websockets
from typing import List, Optional, Dict
import uuid

try:
    import cogency
except ImportError:  # pragma: no cover - optional dependency for live runs
    cogency = None

from ..core.config import Config
from ..core.message import Message
from ..core.protocols import Despawn
from ..core import parser
from ..constitution.coordination import PROTOSS_CONSTITUTION, COORDINATION_PROTOCOL
from ..core.khala import Khala
from ..agents.registry import get_agent_data

logger = logging.getLogger(__name__)


class Agent:
    """Pure constitutional AI coordination agent - data-driven from registry."""

    def __init__(
        self,
        agent_type: str,
        channel: str,
        bus_url: str,
        coordination_id: str,
        config: Config = None,
    ):
        self.agent_type = agent_type
        self.channel = channel
        self.bus_url = bus_url
        self.coordination_id = coordination_id  # New: Store coordination ID
        self.config = config or Config()
        self.khala = Khala(config=self.config)
        self._running = True
        self.agent_id = f"{agent_type}-{uuid.uuid4().hex[:6]}"
        self.identity_index = 0
        self._load_identity()

    def _load_identity(self):
        """Load agent configuration from registry."""
        self.registry_data = get_agent_data(self.agent_type)
        if not self.registry_data:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

    async def _connect_websocket(self):
        """Establishes a connection to the Bus using the Khala."""
        if (
            self.khala
            and self.khala._websocket
            and self.khala._websocket.state == websockets.protocol.State.OPEN
        ):
            return
        try:
            self.khala = Khala(bus_url=self.config.bus_url)
            await self.khala.connect(client_id=f"agent/{self.id}")
            logger.info(f"{self.id} connected to Bus at {self.config.bus_url}")
        except Exception as e:
            logger.error(f"{self.id} failed to connect to Bus: {e}")
            self.khala = None

    async def _receive_message(self, timeout: int = 1) -> Optional[Message]:
        """Receives and parses a single message from the Bus using the Khala with a timeout."""
        if not self.khala:
            logger.warning(f"{self.id} _receive_message called with no khala.")
            return None
        try:
            return await self.khala.receive(timeout=timeout)
        except ConnectionError:
            logger.info(f"{self.id} khala connection closed.")
            self.khala = None
            return None
        except Exception as e:
            logger.error(f"Error receiving message via Khala: {e}")
            self.khala = None
            return None

    def tools(self) -> List:
        """Constitutional tools from registry."""
        tool_categories = self.registry_data.get("tools", [])
        try:
            from cogency.tools import tools

            if isinstance(tool_categories, list):
                return tools.category(tool_categories)
            else:
                return tools.category([tool_categories])
        except ImportError:
            logger.warning(
                f"Cogency not available - {self.agent_type} operating with limited capabilities"
            )
            return []

    def _get_identity(self) -> str:
        """Get identity from registry based on agent type and index."""
        identities = self.registry_data["identity"]
        if len(identities) == 1:
            return identities[0]
        else:
            # Multi-identity case (conclave)
            return identities[self.identity_index]

    async def __call__(self, context: str) -> str:
        """Constitutional Cogency execution with registry-driven configuration."""

        identity = self._get_identity()
        guidelines = self.registry_data["guidelines"]

        instructions = f"""
{PROTOSS_CONSTITUTION}

{identity}

{COORDINATION_PROTOCOL}

{guidelines}
"""

        agent = cogency.Agent(
            llm="openai", instructions=instructions, tools=self.tools()
        )

        response = ""
        async for cogency_event in agent(
            context,
            user_id=f"channel-{self.channel}",
            conversation_id=f"{self.agent_type}-{self.agent_id}",
        ):
            if cogency_event["type"] == "respond":
                content = cogency_event.get("content", "")
                response += content
            await self.broadcast(cogency_event)

        return response

    async def broadcast(self, cogency_event: Dict):
        """Broadcast a cogency event to the Bus using the Khala."""
        if not self.khala or not (
            self.khala._websocket
            and self.khala._websocket.state == websockets.protocol.State.OPEN
        ):
            logger.warning(f"{self.agent_id} khala not open, cannot broadcast event.")
            return

        content = cogency_event.get("content", "")
        event = {
            "type": "agent_message",
            "channel": self.channel,
            "sender": self.agent_id,
            "coordination_id": self.coordination_id,
            "content": content,
            "payload": cogency_event,
            "signals": [s.to_dict() for s in parser.signals(content)],
        }

        try:
            await self.khala.send(event)
        except Exception as e:
            logger.error(f"Error broadcasting event via Khala: {e}")

    def _should_despawn(self, content: str) -> bool:
        """Check if agent output contains !despawn signal."""
        signals = parser.signals(content)
        return any(isinstance(signal, Despawn) for signal in signals)

    async def run(self):
        """Agent main loop."""
        logger.info(
            f"Agent {self.agent_id} ({self.agent_type}) online in {self.channel}"
        )
        await self.khala.connect(bus_url=self.bus_url, agent_id=self.agent_id)
        self.khala.register(self.channel, self.agent_id)

        # Emit agent_spawn event
        await self.send_message(
            content=f"Agent {self.agent_id} ({self.agent_type}) spawned.",
            event_type="agent_spawn",
            event_payload={"agent_id": self.agent_id, "agent_type": self.agent_type},
        )

        try:
            while self._running:
                try:
                    message = await self.khala.recv()
                    if message:
                        await self._process_message(message)
                except asyncio.CancelledError:
                    logger.info(f"Agent {self.agent_id} cancelled.")
                    self._running = False
                except Exception as e:
                    logger.error(f"Agent {self.agent_id} error: {e}")
                    # self._running = False # Consider if agent should stop on any error
                await asyncio.sleep(0.1)  # Yield control
        finally:
            logger.info(f"Agent {self.agent_id} ({self.agent_type}) offline.")
            # Emit agent_despawn event before disconnecting
            await self.send_message(
                content=f"Agent {self.agent_id} ({self.agent_type}) despawned.",
                event_type="agent_despawn",
                event_payload={
                    "agent_id": self.agent_id,
                    "agent_type": self.agent_type,
                },
            )
            await self.khala.disconnect()
