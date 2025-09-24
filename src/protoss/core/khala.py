"""Khala - Sacred telepathic connection to the Bus."""

import asyncio
import json
import websockets
import logging
import time  # Added time import
from typing import List, Dict, Optional

from .message import Message
from .protocols import BaseSignal

logger = logging.getLogger(__name__)


class Khala:
    """Sacred telepathic interface to the Bus coordination network."""

    def __init__(self, bus_url: str):
        self.bus_url = bus_url
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.id: str = "client"

    async def connect(self, client_id: Optional[str] = None):
        """Establish sacred connection to the Bus."""
        if not self.bus_url:
            raise ValueError("Bus URL required for khala connection.")
        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            logger.info(f"Khala already connected to {self.bus_url}")
            return

        try:
            uri = f"{self.bus_url}/{client_id if client_id else self.id}"
            self._websocket = await websockets.connect(uri)
            logger.info(f"Khala connected to Bus at {uri}")
        except Exception as e:
            logger.error(f"Khala failed to connect to Bus at {self.bus_url}: {e}")
            self._websocket = None
            raise ConnectionError(f"Failed to connect to Bus: {e}") from e

    async def disconnect(self):
        """Sever sacred connection to the Bus."""
        if self._websocket:
            await self._websocket.close()
            self._websocket = None
            logger.info("Khala disconnected from Bus.")

    async def send(self, event: Dict):
        """Send a structured event through the sacred channel."""
        if (
            not self._websocket
            or self._websocket.state != websockets.protocol.State.OPEN
        ):
            raise ConnectionError("Not connected to the Bus.")

        # Enrich event with timestamp before sending
        event["timestamp"] = time.time()

        try:
            await self._websocket.send(json.dumps(event))
        except Exception as e:
            logger.error(f"Error sending event via Khala: {e}")
            raise

    def _parse_message(self, message_str: str) -> Message:
        """Parse event dictionary into Message object."""
        event_dict = json.loads(message_str)

        # Handle raw event dictionaries from Bus
        signals = [
            signal
            for s_dict in event_dict.get("signals", [])
            if (signal := BaseSignal.deserialize(s_dict))
        ]

        payload = event_dict.get("payload", {})
        if (
            event_dict.get("content")
            and isinstance(payload, dict)
            and "content" not in payload
        ):
            payload = {**payload, "content": event_dict["content"]}

        return Message(
            sender=event_dict["sender"],
            channel=event_dict["channel"],
            timestamp=event_dict["timestamp"],
            signals=signals,
            event=payload,
            msg_type=event_dict.get("type", "event"),
            coordination_id=event_dict.get("coordination_id"),
        )

    async def receive(self, timeout: int = 1) -> Optional[Message]:
        """Receive message from sacred channel."""
        try:
            if (
                not self._websocket
                or self._websocket.state != websockets.protocol.State.OPEN
            ):
                return None

            message_str = await asyncio.wait_for(
                self._websocket.recv(), timeout=timeout
            )
            return self._parse_message(message_str)
        except asyncio.TimeoutError:
            return None
        except websockets.exceptions.ConnectionClosedOK:
            self._websocket = None
            return None
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            self._websocket = None
            return None

    async def request_history(self, channel_id: str) -> List[Dict]:
        """Request sacred channel history."""
        if (
            not self._websocket
            or self._websocket.state != websockets.protocol.State.OPEN
        ):
            raise ConnectionError("Not connected to the Bus.")

        req = {"type": "history_req", "channel": channel_id}
        await self._websocket.send(json.dumps(req))

        message = await self.receive()
        if (
            message
            and message.msg_type == "history_resp"
            and message.channel == channel_id
        ):
            return message.event.get("history", [])
        else:
            raise ConnectionError("Failed to receive history response from Bus.")

    async def listen(self):
        """Continuous sacred message stream."""
        if (
            not self._websocket
            or self._websocket.state != websockets.protocol.State.OPEN
        ):
            raise ConnectionError("Not connected to the Bus.")

        try:
            async for message_str in self._websocket:
                yield self._parse_message(message_str)
        except websockets.exceptions.ConnectionClosedOK:
            self._websocket = None
        except Exception as e:
            logger.error(f"Error receiving message stream: {e}")
            self._websocket = None
            raise
