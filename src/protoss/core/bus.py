"""A simple, unified message bus for agent coordination."""

import asyncio
import json
import logging
import socket
import time
from typing import Dict, Set, Optional, List
from dataclasses import dataclass, field

import websockets
from .message import Message, Event  # Import Event from message.py
from . import parser
from .protocols import Storage
from protoss.lib.storage import SQLite
from .nexus import Nexus  # Import Nexus

logger = logging.getLogger(__name__)


@dataclass
class Channel:
    """Channel state with history and subscribers."""

    history: List[Message] = field(default_factory=list)
    subscribers: Set[str] = field(default_factory=set)


@dataclass
class Coordination:
    """Lifecycled coordination state tracked by the Bus."""

    channels: Dict[str, Set[str]] = field(default_factory=dict)
    status: str = "active"
    had_agents: bool = False

    def add_agent(self, channel: str, agent_id: str) -> None:
        channel_agents = self.channels.setdefault(channel, set())
        channel_agents.add(agent_id)
        self.had_agents = True

    def remove_agent(self, channel: str, agent_id: str) -> None:
        if channel in self.channels:
            self.channels[channel].discard(agent_id)

    def is_empty(self) -> bool:
        return all(not agents for agents in self.channels.values())


# ==============================================================================
# The Purified Bus Facade
# ==============================================================================


class Bus:
    """A single facade for message routing and coordination.
    Responsibilities are owned explicitly inside the facade."""

    def __init__(
        self,
        nexus: Nexus,  # Inject Nexus
        port: int = 8888,
        storage_path: Optional[str] = None,
    ):
        self.nexus = nexus  # Store Nexus instance
        self.port = port
        self.server: Optional[websockets.WebSocketServer] = None
        self.storage: Storage = SQLite(storage_path or "./.protoss/store.db")

        # State owned by the Bus facade
        self.connections: Dict[str, websockets.ServerProtocol] = {}
        self.channels: Dict[str, Channel] = {}  # Channel state with history

    @property
    def url(self) -> str:
        """Public WebSocket URL for connecting clients."""
        return f"ws://127.0.0.1:{self.port}"

    async def start(self):
        """Starts the WebSocket server."""
        if self.server:
            return
        self.server = await websockets.serve(
            self._handler,
            "127.0.0.1",
            self.port,
            family=socket.AF_INET,
        )
        # Capture the actual port the OS bound when port=0 was requested.
        if self.server.sockets:
            self.port = self.server.sockets[0].getsockname()[1]
        logger.info(f"🔮 Bus online on port {self.port}")

    async def stop(self):
        """Stops the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            logger.info("Bus offline")

    async def transmit(self, channel: str, sender: str, event_type: str, **kwargs):
        """Creates a canonical Event and publishes it to the Nexus."""
        coordination_id = kwargs.pop("coordination_id", None)
        payload = kwargs.pop("event_payload", None) or kwargs.pop("payload", None) or {}
        content = kwargs.pop("content", None) or payload.get("content", "")

        signals = parser.signals(content) if content else []
        message_obj = Message(
            channel=channel,
            sender=sender,
            event=payload,
            msg_type=event_type,
            coordination_id=coordination_id,
            signals=signals,
        )

        event = Event(
            type=event_type,
            channel=channel,
            sender=sender,
            timestamp=message_obj.timestamp,
            payload=payload,
            coordination_id=coordination_id,
            content=content,
            signals=signals,
        )

        channel_state = self.channels.setdefault(channel, Channel())
        channel_state.history.append(message_obj)

        try:
            await self.storage.save_event(event.to_dict())
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to persist event: %s", exc)

        await self.nexus.publish(event)
        await self._broadcast_event(event)  # Still broadcast to external subscribers

    async def _handler(self, websocket: websockets.ServerProtocol):
        """Handles a new agent's WebSocket connection and routes its messages."""
        agent_id = websocket.request.path.lstrip("/")
        self.connections[agent_id] = websocket
        logger.info(f"⚡ {agent_id} connected")
        try:
            async for raw_message in websocket:
                data = json.loads(raw_message)
                channel = data.get("channel")
                if not channel:
                    continue

                event_type = data.get("type", "agent_message")
                coordination_id = data.get("coordination_id")
                content = data.get("content")
                payload = data.get("payload")

                # For now, history requests are still handled here, but will move to Archiver
                if event_type == "history_req":
                    await self._send_history(websocket, channel, data.get("since"))
                    continue

                self.register(channel, agent_id)

                await self.transmit(
                    channel=channel,
                    sender=agent_id,
                    event_type=event_type,
                    coordination_id=coordination_id,
                    content=content,
                    payload=payload,
                )

        except websockets.ConnectionClosed:
            pass
        finally:
            self.connections.pop(agent_id, None)
            # active_units is no longer managed by Bus, so no deregister from there
            logger.info(f"🔌 {agent_id} disconnected")

    async def _broadcast_event(self, event: Event):
        """Broadcast the canonical event to channel subscribers."""
        wire_event = event.to_dict()
        channel = wire_event.get("channel", "")
        sender = wire_event.get("sender", "")
        subscribers = self.channels.get(
            channel, Channel()
        ).subscribers  # Use Bus channel subscribers

        payload = json.dumps(wire_event)
        await asyncio.gather(
            *(
                self.connections[subscriber].send(payload)
                for subscriber in subscribers
                if subscriber != sender and subscriber in self.connections
            ),
            return_exceptions=True,  # Don't fail if one connection is broken
        )

    def register(self, channel: str, agent_id: str):
        """Register agent to channel."""
        if channel not in self.channels:
            self.channels[channel] = Channel()
        self.channels[channel].subscribers.add(agent_id)

    def deregister(self, agent_id: str):
        """Deregister agent from all channels."""
        for channel in self.channels.values():
            channel.subscribers.discard(agent_id)

    async def _send_history(
        self,
        websocket: websockets.ServerProtocol,
        channel: str,
        since: Optional[float] = None,
    ):
        """Respond to history requests with persisted events."""
        # This will eventually query the Archiver
        history = await self.storage.load_events(channel=channel, since=since)
        response = {
            "type": "history_resp",
            "channel": channel,
            "sender": "system",
            "timestamp": time.time(),
            "payload": {"history": history},
        }
        await websocket.send(json.dumps(response))

    async def get_events(
        self, channel: str, since: Optional[float] = None
    ) -> List[Dict]:
        """Retrieves events from storage for a given channel."""
        # This will eventually query the Archiver
        return await self.storage.load_events(channel=channel, since=since)


def main():
    """Entry point for running the Bus as a standalone process."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the Protoss Bus.")
    parser.add_argument("--port", type=int, default=8888, help="Port to run on")
    parser.add_argument(
        "--storage-path", type=str, help="Path to SQLite database file."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Instantiate Nexus and pass to Bus
    nexus = Nexus()
    bus = Bus(nexus=nexus, port=args.port, storage_path=args.storage_path)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bus.start())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Bus shutting down.")
        loop.run_until_complete(bus.stop())


if __name__ == "__main__":
    main()
