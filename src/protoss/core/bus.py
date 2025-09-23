"""Message routing and coordination for distributed agents."""

import asyncio
import json
import logging
import functools
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field, asdict

import websockets
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
        storage_path: Optional[str] = None,
    ):
        """Initialize Bus coordination system."""
        self.channels: Dict[str, Channel] = {}
        self.max_history = max_history
        self.port = port
        self.max_agents = max_agents
        self.storage: Optional[SQLiteStorage] = (
            SQLiteStorage(storage_path) if storage_path else None
        )
        self.active_agents: Dict[str, Set[str]] = {}  # channel -> agent_ids

        # WebSocket server
        self.server = None
        self.connections: Dict[str, websockets.ServerProtocol] = {}

    async def start(self):
        """Start Bus server."""
        if self.server:
            return

        self.server = await websockets.serve(
            functools.partial(self._handler), "localhost", self.port
        )
        logger.info(f"🔮 Bus online on port {self.port}")

    async def stop(self):
        """Stop Bus server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            logger.info("Bus offline")

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
        """Register agent to channel."""
        self._ensure_channel(channel_id)
        self.channels[channel_id].subscribers.add(agent_id)

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
        """Ensure channel exists."""
        if channel_id not in self.channels:
            self.channels[channel_id] = Channel()

    async def _message(self, agent_id: str, raw_message: str):
        """Handle incoming message from agent."""
        data = json.loads(raw_message)
        msg_type = data.get("type", "event")
        channel = data.get("channel", "general")

        if msg_type == "history_req":
            messages = await self.get_history(channel)
            history_events = [msg.event for msg in messages if msg.event]
            response = {
                "type": "history_resp",
                "channel": channel,
                "history": history_events,
            }
            await self._send(agent_id, json.dumps(response))
            return

        event_data = data.get("event")
        if not event_data or not isinstance(event_data, dict):
            return

        content = event_data.get("content", "")
        signals = parser.signals(content)
        await self.transmit(channel, agent_id, event=event_data, signals=signals)

    async def _connect(self, agent_id: str):
        """Handle agent connection."""
        logger.info(f"🔮 {agent_id} connected")

    async def _disconnect(self, agent_id: str):
        """Handle agent disconnection."""
        self.deregister(agent_id)
        logger.info(f"🔌 {agent_id} disconnected")

    async def _broadcast(self, message: Message):
        """Broadcast a message to a channel and handle its side-effects."""
        self._ensure_channel(message.channel)

        self.channels[message.channel].history.append(message)
        if len(self.channels[message.channel].history) > self.max_history:
            self.channels[message.channel].history.pop(0)

        if self.storage:
            await self.storage.save_message(message)

        content = message.event.get("content", "") if message.event else "Signal"
        logger.info(f"⚡ {message.channel} ({message.sender}): {content[:60]}")

        await self._send_to_subscribers(message)

        await self._handle_mentions(message)

    async def _send_to_subscribers(self, message: Message):
        """Send message to channel subscribers."""
        if not self.server:
            return

        subscribers = self.channels.get(message.channel, Channel()).subscribers
        if not subscribers:
            return

        json_payload = json.dumps(asdict(message))

        for agent_id in subscribers:
            if agent_id == message.sender:
                continue

            await self._send(agent_id, json_payload)

    def is_running(self) -> bool:
        """Check if the Bus server is currently running."""
        return self.server is not None

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

    async def _send(self, agent_id: str, message: str):
        """Send message to specific agent."""
        websocket = self.connections.get(agent_id)
        if websocket and (websocket.state == websockets.protocol.State.OPEN):
            await websocket.send(message)

    async def _handler(self, websocket: websockets.ServerProtocol, path: str):
        """Handle websocket connections."""
        agent_id = path.lstrip("/")
        self.connections[agent_id] = websocket

        await self._connect(agent_id)

        try:
            async for message in websocket:
                await self._message(agent_id, message)
        except websockets.ConnectionClosed:
            pass
        finally:
            self.connections.pop(agent_id, None)
            await self._disconnect(agent_id)


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
