"""Message routing and coordination for distributed agents."""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field, asdict

import websockets

from .server import Server
from .message import Message
from . import parser
from .protocols import Signal, Mention
from . import gateway
from protoss.lib.storage import SQLite as SQLiteStorage  # Import SQLiteStorage

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
        port: int = 8888,
        max_history: int = 50,
        max_agents: int = 10,
        storage_path: Optional[str] = None,  # New storage_path parameter
        url: str = None,
    ):
        """Initialize Bus coordination system."""
        # Server mode
        self.server: Optional[Server] = None
        self.channels: Dict[str, Channel] = {}
        self.max_history = max_history
        self.port = port
        self.max_agents = max_agents
        self.storage: Optional[SQLiteStorage] = (
            SQLiteStorage(storage_path) if storage_path else None
        )  # Instantiate SQLiteStorage
        self.active_agents: Dict[str, Set[str]] = {}  # channel -> agent_ids

        # Client mode
        self.url = url
        self.websocket = None

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

        # Track active agents for spawning decisions
        if channel_id not in self.active_agents:
            self.active_agents[channel_id] = set()
        self.active_agents[channel_id].add(agent_id)

    async def get_history(
        self, channel_id: str, since_timestamp: float = 0
    ) -> List[Message]:
        if self.storage:
            return await self.storage.load_messages(channel_id, since_timestamp)

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

        # Remove from active agents tracking
        for channel_agents in self.active_agents.values():
            channel_agents.discard(agent_id)

    def status(self) -> dict:
        return {
            "channels": len(self.channels),
            "agents": sum(len(c.subscribers) for c in self.channels.values()),
            "messages": sum(len(c.history) for c in self.channels.values()),
        }

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
                messages = await self.get_history(channel)
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
        logger.info(f"🔌 {agent_id} disconnected from Bus")

    async def _broadcast(self, message: Message):
        """Broadcast a message to a channel and handle its side-effects."""
        self._ensure_channel(message.channel)

        self.channels[message.channel].history.append(message)
        if len(self.channels[message.channel].history) > self.max_history:
            self.channels[message.channel].history.pop(0)

        if self.storage:
            try:
                await self.storage.save_message(message)
            except Exception as e:
                logger.warning(f"Failed to persist message to storage: {e}")

        logger.info(
            f"⚡ MESSAGE → {message.channel} ({message.sender}): {message.event.get('content', '') if message.event else 'Signal'[:60]}..."
        )

        await self._send_to_subscribers(message)

        await self._handle_mentions(message)

    async def _send_to_subscribers(self, message: Message):
        """Send the message to all agents subscribed to the channel and all monitors."""
        if not self.server:
            return

        subscribers = self.channels.get(message.channel, Channel()).subscribers

        if not subscribers:
            return

        json_payload = json.dumps(asdict(message))

        for agent_id in subscribers:
            if agent_id == message.sender:
                continue

            try:
                await self.server.send(agent_id, json_payload)
            except Exception as e:
                logger.warning(f"Failed to send message to {agent_id}: {e}")

    def is_running(self) -> bool:
        """Check if the Bus server is currently running."""
        return self.server is not None and self.server.is_running()

    async def _handle_mentions(self, message: Message):
        """Handle @mentions by spawning agents if needed."""
        if not message.event or not message.signals:
            return

        for signal in message.signals:
            if isinstance(signal, Mention):
                agent_type = signal.agent_name
                if gateway.should_spawn(
                    agent_type, message.channel, self.active_agents, self.max_agents
                ):
                    try:
                        bus_url = f"ws://localhost:{self.port}"
                        await gateway.spawn_agent(agent_type, message.channel, bus_url)
                        logger.info(
                            f"Spawned {agent_type} for @mention in {message.channel}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to spawn {agent_type}: {e}")

    async def connect(self):
        """Connect to the Bus (client mode)."""
        if not self.url:
            raise ValueError("URL required for client mode")
        self.websocket = await websockets.connect(self.url)

    async def disconnect(self):
        """Disconnect from the Bus (client mode)."""
        if self.websocket:
            await self.websocket.close()

    async def broadcast(
        self, message: str, channel: str = "general", sender: str = "client"
    ):
        """Broadcast a message to a channel (client mode)."""
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
        """Request the history of a channel (client mode)."""
        if not self.websocket:
            raise ConnectionError("Not connected to the Bus.")

        req = {"type": "history_req", "channel": channel_id}
        await self.websocket.send(json.dumps(req))

        response = await self.websocket.recv()
        data = json.loads(response)
        if data.get("type") == "history_resp" and data.get("channel") == channel_id:
            return data.get("history", [])
        return []

    def create_channel(self, channel_id: str):
        """Create a channel (client mode) - channels are created on first message."""
        # Channels are auto-created on first message, no explicit creation needed
        pass


def main():
    """Entry point for running the unified Bus as a standalone process."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the unified Protoss Bus.")
    parser.add_argument("--port", type=int, default=8888, help="Port to run the Bus on")
    parser.add_argument(
        "--max-agents", type=int, default=100, help="Max agents per channel"
    )
    parser.add_argument(
        "--storage-path",
        type=str,
        help="Path to SQLite database file for message history.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    bus = Bus(
        port=args.port, max_agents=args.max_agents, storage_path=args.storage_path
    )

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bus.start())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Constitutional coordination shutting down.")
        loop.run_until_complete(bus.stop())


if __name__ == "__main__":
    main()
