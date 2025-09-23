"""Single Constitutional AI Agent - Data-driven from registry."""

import asyncio
import json
import logging
import websockets
import argparse
from typing import List, Optional, Dict
import uuid

import cogency

from ..core.config import Config
from ..core.message import Message
from ..core.protocols import Signal, Despawn
from ..core import parser
from ..constitution.coordination import PROTOSS_CONSTITUTION, COORDINATION_PROTOCOL
from ..core.khala import Khala

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
        self.identity = []
        self.guidelines = []
        self.tools = []
        self._load_identity()

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

        agent = cogency.Agent(instructions=instructions, tools=self.tools)

        response = ""
        async for event in agent(
            context,
            user_id=f"channel-{self.channel_id}",
            conversation_id=f"{self.agent_type}-{self.id}",
        ):
            if event["type"] == "respond":
                content = event.get("content", "")
                response += content
                await self.broadcast(event)
            elif event["type"] in ["think", "call", "result"]:
                await self.broadcast(event)

        return response

    async def broadcast(
        self,
        content: str = "",
        channel: Optional[str] = None,
        event_type: str = "agent_message",
        event_payload: Optional[Dict] = None,
        signals: Optional[List[Signal]] = None,
    ):
        """Broadcast a structured event to the Bus using the Khala."""
        if not self.khala or not (
            self.khala._websocket
            and self.khala._websocket.state == websockets.protocol.State.OPEN
        ):
            logger.warning(f"{self.agent_id} khala not open, cannot broadcast event.")
            return

        try:
            await self.khala.send(
                channel=channel or self.channel,
                sender=self.agent_id,
                content=content,
                event_type=event_type,
                coordination_id=self.coordination_id,
                event_payload=event_payload,
                signals=signals,
            )
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Constitutional Agent.")
    parser.add_argument("--agent-id", required=True, help="Unique ID for the agent.")
    parser.add_argument("--agent-type", required=True, help="Type of the agent.")
    parser.add_argument("--channel", required=True, help="Channel ID for coordination.")
    parser.add_argument("--bus-url", required=True, help="URL of the Protoss Bus.")
    parser.add_argument(
        "--params",
        default="{}",
        help="JSON string of extra params for agent constructor.",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    async def main():
        config = Config(bus_url=args.bus_url)

        # Prepare constructor arguments
        constructor_args = {
            "agent_id": args.agent_id,
            "agent_type": args.agent_type,
            "channel_id": args.channel,
            "config": config,
        }

        # Add extra parameters from the command line
        try:
            extra_params = json.loads(args.params)
            constructor_args.update(extra_params)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in --params: {args.params}")
            return

        # Create agent instance
        agent = Agent(**constructor_args)

        await agent._connect_websocket()
        try:
            logger.info(f"{agent.id} starting coordinate loop")
            await agent.coordinate()
        except KeyboardInterrupt:
            logger.info(f"{agent.id} interrupted.")
        finally:
            if agent.khala:
                await agent.khala.disconnect()

    asyncio.run(main())
