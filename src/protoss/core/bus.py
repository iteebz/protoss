"""Message routing and coordination for distributed agents."""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

from .server import Server
from .message import Message
from . import parser
from .protocols import Signal

logger = logging.getLogger(__name__)


@dataclass
class Channel:
    """Represents a single coordination channel."""

    subscribers: Set[str] = field(default_factory=set)
    history: List[Message] = field(default_factory=list)


class Bus:
    """Message routing and coordination for distributed agents."""

    def __init__(
        self,
        port: int = None,
        max_history: int = 50,
        storage=None,
        spawner=None,
        max_agents: Optional[int] = None,
        enable_storage: bool = True,
        storage_base_dir: Optional[str] = None,
    ):
        """Initialize Bus coordination system."""
        self.server: Optional[Server] = None
        self.channels: Dict[str, Channel] = {}
        self.monitor_clients: Set[str] = set()
        self.max_history = max_history
        self.port = port or 8888
        self.storage = self._init_storage(storage, enable_storage, storage_base_dir)
        self.completion_watchers: Dict[str, str] = {}


class BusClient:
    """A client for interacting with the Protoss Bus."""

    def __init__(self, url: str):
        self.url = url
        self.websocket: websockets.WebSocketClientProtocol = None

    async def connect(self):
        """Connect to the Bus."""
        self.websocket = await websockets.connect(self.url)

    async def disconnect(self):
        """Disconnect from the Bus."""
        if self.websocket:
            await self.websocket.close()

    async def broadcast(self, message: str, channel: str, sender: str):
        """Broadcast a message to a channel."""
        if not self.websocket:
            raise ConnectionError("Not connected to the Bus.")

        msg = {
            "type": "event",
            "channel": channel,
            "sender": sender,
            "event": {"content": message},
        }
        await self.websocket.send(json.dumps(msg))

    async def history(self, channel_id: str) -> List[Dict]:
        """Request the history of a channel."""
        if not self.websocket:
            raise ConnectionError("Not connected to the Bus.")

        req = {"type": "history_req", "channel": channel_id}
        await self.websocket.send(json.dumps(req))

        # Wait for the response
        response = await self.websocket.recv()
        data = json.loads(response)
        if data.get("type") == "history_resp" and data.get("channel") == channel_id:
            return data.get("history", [])
        return []

    def create_channel(self, channel_id: str):
        """Request the creation of a channel."""
        # This is a bit of a hack. The client is sending a message to the bus
        # that it will then have to handle in the _message method.
        # This is not ideal, but it's the simplest way to implement this
        # without changing the bus server.
        if not self.websocket:
            raise ConnectionError("Not connected to the Bus.")

        msg = {
            "type": "system",
            "channel": "general",
            "sender": "BusClient",
            "event": {"content": f"!create_channel {channel_id}"},
        }
        asyncio.create_task(self.websocket.send(json.dumps(msg)))

    async def start(self):
        if self.server is None:
            self.server = Server(self.port)
            self.server.on_message(self._message)
            self.server.on_connect(self._connect)
            self.server.on_disconnect(self._disconnect)
            await self.server.start()
            logger.info("🔮 Bus coordination network online")

    async def stop(self):
        if self.server:
            await self.server.stop()
            self.server = None

    async def transmit(
        self,
        channel: str,
        sender: str,
        event: Optional[Dict] = None,
        signals: Optional[List[Signal]] = None,
    ):
        message = Message(channel=channel, sender=sender, event=event, signals=signals)
        await self._broadcast(message)

    def register(self, channel_id: str, agent_id: str):
        logger.debug(f"Agent {agent_id} attempting to register to channel {channel_id}")
        self._ensure_channel(channel_id)
        self.channels[channel_id].subscribers.add(agent_id)

    def history(self, channel_id: str, since_timestamp: float = 0) -> List[Message]:
        if channel_id not in self.channels:
            return []
        return [
            msg
            for msg in self.channels[channel_id].history
            if msg.timestamp > since_timestamp
        ]

    def deregister(self, agent_id: str):
        for channel in self.channels.values():
            channel.subscribers.discard(agent_id)

    def status(self) -> dict:
        return {
            "channels": len(self.channels),
            "agents": sum(len(c.subscribers) for c in self.channels.values()),
            "messages": sum(len(c.history) for c in self.channels.values()),
        }

    def _init_storage(
        self,
        storage,
        enable_storage: bool,
        base_dir: Optional[str],
    ):
        """Initialize storage backend based on configuration."""
        if storage is not None:
            return storage
        if not enable_storage:
            return None
        try:
            from ..lib.storage import SQLite

            return SQLite(base_dir=base_dir)
        except Exception as exc:
            logger.warning(
                f"⚠️ Storage initialization failed ({exc}); continuing without persistence"
            )
            return None

    def _ensure_channel(self, channel_id: str):
        """Guarantee channel bookkeeping exists."""
        if channel_id not in self.channels:
            self.channels[channel_id] = Channel()
            logger.info(f"🔮 Bus channel opened: {channel_id}")

    async def _message(self, agent_id: str, raw_message: str):
        """Handle incoming WebSocket message from an agent."""
        logger.debug(f"Received message from {agent_id}: {raw_message}")
        try:
            data = json.loads(raw_message)
            msg_type = data.get("type", "event")  # Default to event-based communication
            channel = data.get("channel", "general")

            if msg_type == "history_req":
                messages = self.history(channel)
                history_events = [msg.event for msg in messages if msg.event]
                response = {
                    "type": "history_resp",
                    "channel": channel,
                    "history": history_events,
                }
                if self.server:
                    await self.server.send(agent_id, json.dumps(response))
                return

            event_data = data.get("event")
            if event_data is None or not isinstance(event_data, dict):
                logger.warning(f"Message from {agent_id} has no valid event data.")
                return

            # Per emergence.md, signals are parsed from the content of the event.
            content = event_data.get("content", "")
            signals = parser.signals(content)

            await self.transmit(channel, agent_id, event=event_data, signals=signals)

        except json.JSONDecodeError:
            logger.warning(f"Received invalid JSON from {agent_id}: {raw_message}")
        except Exception as e:
            logger.error(f"Error processing message from {agent_id}: {e}")

    async def _connect(self, agent_id: str):
        """Handle agent connection to coordination network."""
        logger.info(f"🔮 {agent_id} connected to Khala")

    async def _disconnect(self, agent_id: str):
        """Handle agent disconnection from coordination network."""
        self.deregister(agent_id)
        self.monitor_clients.discard(agent_id)
        logger.info(f"🔌 {agent_id} disconnected from Bus")

    async def _broadcast(self, message: Message):
        """Broadcast a message to a channel and handle its side-effects."""
        self._ensure_channel(message.channel)

        # Append to in-memory history and handle pruning.
        self.channels[message.channel].history.append(message)
        if len(self.channels[message.channel].history) > self.max_history:
            self.channels[message.channel].history.pop(0)

        # Persist if storage is enabled.
        if self.storage:
            try:
                await self.storage.save_message(message)
            except Exception as e:
                logger.warning(f"Failed to persist message to storage: {e}")

        logger.info(
            f"⚡ MESSAGE → {message.channel} ({message.sender}): {message.event.get('content', '') if message.event else 'Signal'[:60]}..."
        )

        await self._send_to_subscribers(message)

    async def _send_to_subscribers(self, message: Message):
        """Send the message to all agents subscribed to the channel and all monitors."""
        if not self.server:
            return

        # Per emergence.md, the Bus is an impartial medium. It broadcasts the full
        # message to all subscribers of the channel, plus any system-wide monitors.
        subscribers_in_channel = self.channels.get(
            message.channel, Channel()
        ).subscribers
        all_targets = set(subscribers_in_channel) | self.monitor_clients

        if not all_targets:
            return

        # Serialize the full message once for all targets.
        json_payload = message.serialize()

        for agent_id in all_targets:
            if agent_id == message.sender:
                continue  # Don't send messages back to the sender.

            try:
                await self.server.send(agent_id, json_payload)
            except Exception as e:
                logger.warning(f"Failed to send message to {agent_id}: {e}")

    def is_running(self) -> bool:
        """Check if the Bus server is currently running."""
        return self.server is not None and self.server.is_running()


def main():
    """Entry point for running the Bus as a standalone process."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the Protoss Bus.")
    parser.add_argument("--port", type=int, default=8888, help="Port to run the Bus on")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    bus = Bus(port=args.port)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bus.start())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Bus shutting down.")
        loop.run_until_complete(bus.stop())


if __name__ == "__main__":
    main()
