"""The Cathedral Interface: Constitutional coordination as architectural poetry."""

import asyncio
import json
import logging
import websockets
import uuid
from typing import Any, Optional
from ..core.config import Config

logger = logging.getLogger(__name__)


class Protoss:
    """The Cathedral Interface for constitutional AI swarm coordination.

    This class provides the primary entry point for interacting with the Protoss
    system, enabling users to define a 'vision' (task) and engage with the swarm
    through an asynchronous context manager.

    The `Protoss` class embodies the constitutional principle of the Cathedral
    Interface, offering a simple yet powerful way to initiate and oversee
    constitutional AI coordination.
    """

    def __init__(self, vision: str, config: Config):
        self.vision = vision
        self.config = config
        self._channel_id = f"cathedral_{uuid.uuid4().hex[:8]}"
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        logger.info(f"Protoss instance created for vision: {vision}")

    async def __aenter__(self) -> "Protoss":
        """Constitutional infrastructure genesis."""
        logger.info(
            f"Initializing constitutional coordination for vision: {self.vision}"
        )

        # Connect to the Bus
        uri = f"{self.config.bus_url}/protoss_engine"
        self._websocket = await websockets.connect(uri)
        logger.info("Connected to the Bus.")

        # Register as an engine client
        await self._websocket.send(json.dumps({"type": "engine_req"}))
        ack = await self._websocket.recv()
        if json.loads(ack).get("type") == "engine_ack":
            logger.info("Registered as engine client.")
        else:
            raise ConnectionRefusedError("Failed to register as engine client.")

        # Seed the initial vision onto the Bus
        vision_message = {
            "type": "vision",
            "channel": self._channel_id,
            "content": self.vision,
            "params": {},  # Future: allow initial parameters for vision
        }
        await self._transmit("msg", "gateway_commands", vision_message)
        logger.info(f"Initial vision '{self.vision}' seeded onto the Bus.")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Constitutional infrastructure dissolution."""
        logger.info("Dissolving constitutional coordination.")
        if self._websocket:
            await self._websocket.close()
            logger.info("Disconnected from the Bus.")

    async def _transmit(self, msg_type: str, channel: str, content: Any):
        """Transmit a message to the Bus."""
        if self._websocket and self._websocket.open:
            message = {"type": msg_type, "channel": channel, "content": content}
            await self._websocket.send(json.dumps(message))
        else:
            logger.warning("WebSocket not connected. Message not transmitted.")

    async def _await_completion(self):
        """Await the completion of the constitutional coordination."""
        logger.info(f"Awaiting completion for channel {self._channel_id}...")
        # This is a placeholder. Real implementation would involve listening
        # for completion signals on the Bus.
        while True:
            try:
                message = await self._websocket.recv()
                parsed_message = json.loads(message)
                if (
                    parsed_message.get("type") == "signal"
                    and parsed_message.get("content") == "complete"
                    and parsed_message.get("channel") == self._channel_id
                ):
                    logger.info(
                        f"Completion signal received for channel {self._channel_id}."
                    )
                    break
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Bus connection closed while awaiting completion.")
                break
            except Exception as e:
                logger.error(f"Error while awaiting completion: {e}")
                break
            await asyncio.sleep(0.1)  # Prevent busy-waiting
