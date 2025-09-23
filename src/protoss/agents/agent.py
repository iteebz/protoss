"""Single Constitutional AI Agent - Data-driven from registry."""

import asyncio
import json
import logging
import websockets
import argparse
from typing import List, Optional, Dict
from dataclasses import asdict

from ..core.config import Config
from ..core.message import Message
from ..core.protocols import Signal, Despawn, deserialize_signal
from ..core import parser
from ..constitution.coordination import PROTOSS_CONSTITUTION, COORDINATION_PROTOCOL
from .registry import AGENT_REGISTRY

logger = logging.getLogger(__name__)


class Agent:
    """Pure constitutional AI coordination agent - data-driven from registry."""

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        channel_id: str,
        config: Config,
        identity_index: int = 0,
    ):
        self.id = agent_id
        self.agent_type = agent_type
        self.channel_id = channel_id
        self.config = config
        self.identity_index = identity_index  # For conclave multi-identity
        self._websocket = None

        if agent_type not in AGENT_REGISTRY:
            raise ValueError(f"Unknown agent type: {agent_type}")

        self.registry_data = AGENT_REGISTRY[agent_type]

    async def _connect_websocket(self):
        """Establishes a websocket connection to the Bus for receiving messages."""
        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            return
        try:
            uri = f"{self.config.bus_url}/agent/{self.id}"
            self._websocket = await websockets.connect(uri)
            logger.info(f"{self.id} connected to Bus at {uri}")
        except Exception as e:
            logger.error(f"{self.id} failed to connect to Bus: {e}")
            self._websocket = None

    async def _receive_message(self, timeout: int = 1) -> Optional[Message]:
        """Receives and parses a single message from the websocket with a timeout."""
        try:
            if (
                not self._websocket
                or self._websocket.state != websockets.protocol.State.OPEN
            ):
                logger.warning(
                    f"{self.id} _receive_message called with closed websocket."
                )
                return None

            message_str = await asyncio.wait_for(
                self._websocket.recv(), timeout=timeout
            )
            message_dict = json.loads(message_str)

            reconstructed_signals = [
                signal
                for s_dict in message_dict.get("signals", [])
                if (signal := deserialize_signal(s_dict))
            ]

            return Message(
                sender=message_dict["sender"],
                channel=message_dict["channel"],
                timestamp=message_dict["timestamp"],
                signals=reconstructed_signals,
                event=message_dict["event"],
            )
        except asyncio.TimeoutError:
            return None
        except websockets.exceptions.ConnectionClosedOK:
            logger.info(f"{self.id} websocket connection closed.")
            self._websocket = None
            return None
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            self._websocket = None
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
        from cogency.core.agent import Agent as CogencyAgent

        identity = self._get_identity()
        guidelines = self.registry_data["guidelines"]

        instructions = f"""
{PROTOSS_CONSTITUTION}

{identity}

{COORDINATION_PROTOCOL}

{guidelines}
"""

        agent = CogencyAgent(instructions=instructions, tools=self.tools)

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
        self, event: Optional[Dict] = None, signals: Optional[List[Signal]] = None
    ):
        """Broadcast a structured message to the Bus."""
        if not self._websocket or not (
            self._websocket.state == websockets.protocol.State.OPEN
        ):
            logger.warning(f"{self.id} websocket not open, cannot broadcast message.")
            return

        message_to_send = Message(
            channel=self.channel_id,
            sender=self.id,
            event=event,
            signals=signals if signals is not None else [],
        )
        try:
            await self._websocket.send(json.dumps(asdict(message_to_send)))
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

    def _should_despawn(self, content: str) -> bool:
        """Check if agent output contains !despawn signal."""
        signals = parser.signals(content)
        return any(isinstance(signal, Despawn) for signal in signals)

    async def coordinate(self):
        """The main coordination loop for agents that require continuous interaction."""
        logger.info(f"{self.id} starting coordinate loop.")
        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 5

        while True:
            try:
                message = await self._receive_message()
                if message:
                    consecutive_errors = 0
                    response = await self(message.event.get("content", ""))

                    if response and self._should_despawn(response):
                        logger.info(
                            f"{self.id} detected !despawn in own response - terminating"
                        )
                        break

            except websockets.exceptions.ConnectionClosedOK:
                break
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    logger.critical(
                        f"{self.id} experienced {consecutive_errors} consecutive errors. Despawning: {e}"
                    )
                    break
                else:
                    logger.error(
                        f"{self.id} error in coordinate loop (consecutive: {consecutive_errors}): {e}"
                    )
            await asyncio.sleep(0.1)

        logger.info(f"{self.id} coordinate loop ended - agent despawning")


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
        agent_instance = Agent(**constructor_args)

        await agent_instance._connect_websocket()
        try:
            logger.info(f"{agent_instance.id} starting coordinate loop")
            await agent_instance.coordinate()
        except KeyboardInterrupt:
            logger.info(f"{agent_instance.id} interrupted.")
        finally:
            if agent_instance._websocket:
                await agent_instance._websocket.close()

    asyncio.run(main())
