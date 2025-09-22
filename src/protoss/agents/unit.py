import asyncio
import json
import logging
import websockets
import argparse
from typing import List, Optional, Dict
from dataclasses import asdict

from ..core.config import Config
from ..core.message import Message
from ..core.protocols import Signal
from ..core import parser
import time

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
            # Reconstruct Message object from dict
            # Note: This assumes signals are serialized as dicts and need to be reconstructed into Signal objects
            reconstructed_signals = []
            for s_dict in message_dict.get("signals", []):
                # This is a placeholder; proper deserialization of polymorphic Signals needs a registry
                # For now, we'll assume a simple Signal base class reconstruction or pass as dict
                reconstructed_signals.append(
                    Signal(**s_dict)
                )  # This will likely fail for subclasses

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

    async def poll_channel_for_response(
        self,
        timeout: int = 10,
        sender_filter: Optional[str] = None,
        content_filter: Optional[str] = None,
        signal_type_filter: Optional[type] = None,
    ) -> Optional[Message]:
        """Polls the channel for a message that matches the given filters."""
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            message = await self._receive_message(
                timeout=1
            )  # Short timeout for polling
            if message is None:
                continue

            # Apply filters
            if sender_filter and message.sender != sender_filter:
                continue
            if content_filter and (
                not message.event
                or content_filter not in message.event.get("content", "")
            ):
                continue

            # For signal_type_filter, we check the message.signals list
            if signal_type_filter:
                if not any(isinstance(s, signal_type_filter) for s in message.signals):
                    continue

            logger.debug(f"{self.id} received matching message: {message}")
            return message
        logger.info(f"{self.id} timed out polling for message.")
        return None

    @property
    def identity(self) -> str:
        """Pure constitutional identity from constitution/ namespace. Override this."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement identity")

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

    async def _connect_to_bus(self):
        """Establish WebSocket connection to the Bus."""
        uri = f"{self.config.bus_url}/{self.agent_id}"
        try:
            self._websocket = await websockets.connect(uri)
            logger.info(f"{self.agent_id} connected to Bus at {self.config.bus_url}")
            # Register with the bus
            await self._websocket.send(
                json.dumps({"type": "join_channel", "channel": self.channel_id})
            )
        except Exception as e:
            logger.error(f"{self.agent_id} failed to connect to Bus: {e}")
            self._websocket = None

    async def _disconnect_from_bus(self):
        """Close WebSocket connection to the Bus."""
        if self._websocket and (
            self._websocket.state == websockets.protocol.State.OPEN
        ):
            await self._websocket.close()
            logger.info(f"{self.agent_id} disconnected from Bus.")
        self._websocket = None

    @abstractmethod
    async def __call__(self, context: str) -> str:
        """The agent's primary execution method, receiving context and returning a response."""
        pass

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

    async def coordinate(self):
        """The main coordination loop for agents that require continuous interaction."""
        logger.info(f"{self.id} starting coordinate loop.")
        while True:
            try:
                message = await self._receive_message()
                if message:
                    # Invoke the agent's __call__ method with the new message content
                    await self(message.event.get("content", ""))
            except websockets.exceptions.ConnectionClosedOK:
                break  # Exit loop if connection is closed
            except Exception as e:
                logger.error(f"{self.id} error in coordinate loop: {e}")
            await asyncio.sleep(0.1)  # Prevent busy-waiting


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Protoss Unit agent.")
    parser.add_argument("--agent-id", required=True, help="Unique ID for the agent.")
    parser.add_argument(
        "--agent-type", required=True, help="Type of the agent (e.g., zealot, archon)."
    )
    parser.add_argument("--channel", required=True, help="Channel ID for coordination.")
    parser.add_argument("--bus-url", required=True, help="URL of the Protoss Bus.")
    parser.add_argument("--task", required=True, help="The task context for the agent.")
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
        from .conclave import Conclave

        agent_classes = {
            "zealot": Zealot,
            "archon": Archon,
            "arbiter": Arbiter,
            "conclave": Conclave,
        }

        agent_class = agent_classes.get(args.agent_type)
        if not agent_class:
            logger.error(f"Unknown agent type: {args.agent_type}")
            return

        config = Config().with_overrides(bus_url=args.bus_url)

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

        await agent_instance._connect_to_bus()
        try:
            logger.info(
                f"{agent_instance.id} starting with initial context: {args.task}"
            )
            await agent_instance(args.task)  # Call the agent with the initial task

            # Only Zealots and Conclaves run the continuous coordinate loop
            if agent_instance.agent_type in ["zealot", "conclave"]:
                await agent_instance.coordinate()

        except KeyboardInterrupt:
            logger.info(f"{agent_instance.agent_id} interrupted.")
        finally:
            await agent_instance._disconnect_from_bus()

    asyncio.run(main())
