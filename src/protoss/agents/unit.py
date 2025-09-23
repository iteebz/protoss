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
from ..constitution import AGENT_IDENTITIES, PROTOSS_CONSTITUTION, COORDINATION_PROTOCOL

logger = logging.getLogger(__name__)


class Unit:
    """Pure constitutional AI coordination agent interface."""

    def __init__(self, agent_id: str, agent_type: str, channel_id: str, config: Config):
        self.id = agent_id
        self.agent_type = agent_type
        self.channel_id = channel_id
        self.config = config
        self._websocket = None  # Agent's own websocket for receiving

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

    @property
    def tools(self) -> List:
        """Constitutional tools. Override if needed."""
        return []

    def _cogency_tools(self, tool_names: List[str]) -> List:
        """Helper to import cogency tools with graceful degradation."""
        try:
            from cogency.tools import TOOLS

            requested_tools = [tool for tool in TOOLS if tool.name in tool_names]
            if not requested_tools:
                logger.warning(f"No matching tools found for {tool_names}")
            return requested_tools
        except ImportError:
            logger.warning(
                f"Cogency not available - {self.__class__.__name__} operating with limited capabilities"
            )
            return []

    async def __call__(self, context: str) -> str:
        """Constitutional Cogency execution with identity from AGENT_IDENTITIES mapping."""
        from cogency.core.agent import Agent

        # Get identity from constitutional mapping
        if self.agent_type in AGENT_IDENTITIES:
            agent_identities = AGENT_IDENTITIES[self.agent_type]
            if isinstance(agent_identities, list):
                # This shouldn't happen for base Unit usage, but handle gracefully
                raise ValueError(
                    f"Agent type {self.agent_type} requires special handling"
                )
            identity = agent_identities
        else:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

        instructions = f"""
{PROTOSS_CONSTITUTION}

{identity}

{COORDINATION_PROTOCOL}
"""

        agent = Agent(instructions=instructions, tools=self.tools)

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
            # Serialize Message dataclass to dict for JSON transmission
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
        MAX_CONSECUTIVE_ERRORS = 5  # Constitutional limit for agent errors

        while True:
            try:
                message = await self._receive_message()
                if message:
                    consecutive_errors = 0  # Reset on successful message processing
                    # Invoke the agent's __call__ method with the new message content
                    response = await self(message.event.get("content", ""))

                    # Check if agent wants to despawn
                    if response and self._should_despawn(response):
                        logger.info(
                            f"{self.id} detected !despawn in own response - terminating"
                        )
                        break

            except websockets.exceptions.ConnectionClosedOK:
                break  # Exit loop if connection is closed
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    logger.critical(
                        f"{self.id} experienced {consecutive_errors} consecutive errors. Despawning due to persistent failure: {e}"
                    )
                    break  # Despawn the agent
                else:
                    logger.error(
                        f"{self.id} error in coordinate loop (consecutive: {consecutive_errors}): {e}"
                    )
            await asyncio.sleep(0.1)  # Prevent busy-waiting

        logger.info(f"{self.id} coordinate loop ended - agent despawning")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Protoss Unit agent.")
    parser.add_argument("--agent-id", required=True, help="Unique ID for the agent.")
    parser.add_argument(
        "--agent-type", required=True, help="Type of the agent (e.g., zealot, archon)."
    )
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
        from .zealot import Zealot
        from .archon import Archon
        from .arbiter import Arbiter
        from .oracle import Oracle

        agent_classes = {
            "zealot": Zealot,
            "archon": Archon,
            "arbiter": Arbiter,
            "oracle": Oracle,
        }

        agent_class = agent_classes.get(args.agent_type)
        if not agent_class:
            logger.error(f"Unknown agent type: {args.agent_type}")
            return

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

        # Create agent instance with all arguments
        agent_instance = agent_class(**constructor_args)

        await agent_instance._connect_websocket()
        try:
            logger.info(f"{agent_instance.id} starting coordinate loop")
            # Agent orients from channel context per emergence.md
            await agent_instance.coordinate()

        except KeyboardInterrupt:
            logger.info(f"{agent_instance.id} interrupted.")
        finally:
            if agent_instance._websocket:
                await agent_instance._websocket.close()

    asyncio.run(main())
