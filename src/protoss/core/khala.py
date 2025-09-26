"""Khala - Sacred telepathic connection to the Bus."""

import asyncio
import json
import websockets
import logging
import time  # Added time import
from typing import List, Dict, Optional

from .event import Event
from .protocols import BaseSignal

logger = logging.getLogger(__name__)


class Khala:
    """Sacred telepathic interface to the Bus coordination network."""

    def __init__(self, bus_url: str):
        self.bus_url = bus_url
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.id: str = "client"

    async def connect(self, agent_id: Optional[str] = None):
        if self._websocket:
            logger.warning("Already connected.")
            return

        # Append agent_id to the URL path for server-side identification
        url = f"{self.bus_url}/{agent_id}" if agent_id else self.bus_url
        try:
            self._websocket = await websockets.connect(url)
            self.id = agent_id or "client"
            logger.info(f"Khala connected to Bus as {self.id}.")
        except Exception as e:
            logger.error(f"Failed to connect to Bus: {e}")
            self._websocket = None

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

        logger.info(f"Khala sending event: {event}")

        try:
            await self._websocket.send(json.dumps(event))
            logger.info("Khala event sent successfully to Bus")
        except Exception as e:
            logger.error(f"Error sending event via Khala: {e}")
            raise

    def _parse_message(self, message_str: str) -> Event:
        """Parse event dictionary into Event object."""
        event_dict = json.loads(message_str)

        signals = [
            signal
            for s_dict in event_dict.get("signals", [])
            if (signal := BaseSignal.deserialize(s_dict))
        ]

        payload = event_dict.get("payload", {})
        content = event_dict.get("content")

        return Event(
            type=event_dict.get("type", "event"),
            channel=event_dict["channel"],
            sender=event_dict["sender"],
            timestamp=event_dict["timestamp"],
            payload=payload,
            coordination_id=event_dict.get("coordination_id"),
            content=content,
            signals=signals,
        )

    async def receive(self, timeout: int = 1) -> Optional[Event]:
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

        event = await self.receive(timeout=5)
        if event and event.type == "history_resp" and event.channel == channel_id:
            return event.payload.get("history", [])
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
