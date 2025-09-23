"""Message routing and coordination for distributed agents."""

import asyncio
import json
import logging
import time
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field, asdict

import websockets
from .message import Message
from . import parser
from .protocols import Signal, Mention
from . import gateway
from .protocols import Storage
from protoss.lib.storage import SQLite

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
        # Initialize storage backend (defaulting to SQLite)
        self.storage: Storage = SQLite(storage_path or "./.protoss/store.db")
        self.active_agents: Dict[str, Set[str]] = {}  # channel -> agent_ids
        self.active_coordinations: Dict[
            str, Dict[str, Set[str]]
        ] = {}  # coordination_id -> {channel -> agent_ids}
        self.coordination_status: Dict[
            str, str
        ] = {}  # coordination_id -> status (e.g., "active", "complete")

        # WebSocket server
        self.server = None
        self.connections: Dict[str, websockets.ServerProtocol] = {}

    async def start(self):
        """Start Bus server."""
        if self.server:
            return

        self.server = await websockets.serve(self._handler, "localhost", self.port)
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
        event_type: str = "agent_message",
        coordination_id: Optional[str] = None,
        event_payload: Optional[Dict] = None,
        signals: Optional[List[Signal]] = None,
    ):
        # Create the Message object
        message = Message(
            channel=channel, sender=sender, event=event_payload, signals=signals or []
        )

        # Create the structured event dictionary
        structured_event = {
            "type": event_type,
            "channel": channel,
            "sender": sender,
            "timestamp": message.timestamp,
            "coordination_id": coordination_id,
            "message": asdict(message),  # Include the full message as a dictionary
            "payload": event_payload,  # Include the payload directly in the event
        }
        await self._broadcast(structured_event)

    def register(self, channel_id: str, agent_id: str):
        """Register agent to channel."""
        self._ensure_channel(channel_id)
        self.channels[channel_id].subscribers.add(agent_id)

        if channel_id not in self.active_agents:
            self.active_agents[channel_id] = set()
        self.active_agents[channel_id].add(agent_id)

    async def get_events(self, **kwargs) -> List[Dict]:
        """Get events from storage."""
        return await self.storage.load_events(**kwargs)

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
        event_type = data.get("type", "agent_message")  # Default to agent_message
        channel = data.get("channel", "general")
        coordination_id = data.get("coordination_id")

        # Handle system requests (status, history)
        if event_type == "status_req":
            bus_metrics = self.status()
            response_event = {
                "type": "status_resp",
                "channel": channel,
                "sender": "system",
                "timestamp": time.time(),
                "payload": {"status": "online", "bus": bus_metrics},
            }
            await self._send(agent_id, response_event)
            return

        if event_type == "history_req":
            events = await self.get_events(channel=channel)
            response_event = {
                "type": "history_resp",
                "channel": channel,
                "sender": "system",
                "timestamp": time.time(),
                "payload": {"history": events},
            }
            await self._send(agent_id, response_event)
            return

        # For agent-generated events, extract content and signals
        content = data.get("content", "")
        signals = parser.signals(content)

        # Create event payload with content
        payload = data.get("payload", {})
        if content:
            payload["content"] = content

        # Transmit the structured event
        await self.transmit(
            channel=channel,
            sender=agent_id,
            event_type=event_type,
            coordination_id=coordination_id,
            event_payload=payload,
            signals=signals,
        )

    async def _connect(self, agent_id: str):
        """Handle agent connection and emit agent_connected event."""
        logger.info(f"🔮 {agent_id} connected")
        await self.transmit(
            channel="system",  # System channel for connection events
            sender=agent_id,
            event_type="agent_connected",
            event_payload={"agent_id": agent_id},
        )

    async def _disconnect(self, agent_id: str):
        """Handle agent disconnection and emit agent_disconnected event."""
        self.deregister(agent_id)
        logger.info(f"🔌 {agent_id} disconnected")
        await self.transmit(
            channel="system",  # System channel for disconnection events
            sender=agent_id,
            event_type="agent_disconnected",
            event_payload={"agent_id": agent_id},
        )

    async def _broadcast(self, event: Dict):
        """Broadcast a structured event to relevant subscribers and handle its side-effects."""
        event_type = event.get("type", "unknown")
        channel = event.get("channel", "general")
        sender = event.get("sender", "system")
        event.get("coordination_id")  # New field for tracking

        self._ensure_channel(channel)

        # Store message in history if it's a message event
        if event_type == "agent_message" and "message" in event:
            message = event["message"]
            self.channels[channel].history.append(message)
            if len(self.channels[channel].history) > self.max_history:
                self.channels[channel].history.pop(0)
            content = message.event.get("content", "") if message.event else "Signal"
            logger.info(f"⚡ {channel} ({sender}): {content[:60]}")
        else:
            logger.info(f"⚡ {channel} ({sender}): {event_type} event")

        # Save ALL events to storage
        logger.info(f"🔍 Saving event to storage: {event_type}")
        try:
            await self.storage.save_event(event)
            logger.info("✅ Event saved successfully")
        except Exception as e:
            logger.error(f"❌ Failed to save event: {e}")
            import traceback

            traceback.print_exc()

        # Send the raw event dictionary to all subscribers
        await self._send_to_subscribers(event)

        # Handle mentions only for agent_message events
        if event_type == "agent_message" and "message" in event:
            await self._handle_mentions(event["message"])

        # Facilitate coordination lifecycle events
        await self._coordinate_lifecycle(event)

    async def _send_to_subscribers(self, event: Dict):
        """Send event to channel subscribers."""
        if not self.server:
            return

        channel = event.get("channel", "general")
        sender = event.get("sender", "system")

        subscribers = self.channels.get(channel, Channel()).subscribers
        if not subscribers:
            return

        json.dumps(event)  # Send the raw event dictionary

        for agent_id in subscribers:
            if agent_id == sender:  # Don't send event back to sender
                continue

            await self._send(agent_id, event)  # Pass the event dictionary directly

    def is_running(self) -> bool:
        """Check if the Bus server is currently running."""
        return self.server is not None

    async def _handle_mentions(self, event: Dict):
        """Handle @mentions by spawning agents if needed."""
        message = event.get("message")
        if not message or not message.get("event") or not message.get("signals"):
            return

        for signal in message["signals"]:
            if isinstance(signal, Mention):
                agent_type = signal.agent_name
                if gateway.should_spawn(
                    agent_type, message["channel"], self.active_agents, self.max_agents
                ):
                    try:
                        bus_url = f"ws://localhost:{self.port}"
                        await gateway.spawn_agent(
                            agent_type, message["channel"], bus_url
                        )
                        logger.info(
                            f"Spawned {agent_type} for @mention in {message["channel"]}"
                        )
                        # Emit agent_spawn event
                        await self.transmit(
                            channel=message["channel"],
                            sender=agent_type,  # The newly spawned agent is the sender
                            event_type="agent_spawn",
                            coordination_id=event.get("coordination_id"),
                            event_payload={
                                "agent_type": agent_type,
                                "spawned_by": message["sender"],
                            },
                        )
                    except Exception as e:
                        logger.error(f"Failed to spawn {agent_type}: {e}")

    async def _coordinate_lifecycle(self, event: Dict):
        """Facilitates the lifecycle of coordination sessions based on events."""
        event_type = event.get("type")
        coordination_id = event.get("coordination_id")
        sender = event.get("sender")
        channel = event.get("channel")

        if not coordination_id:
            return  # Only track events with a coordination_id

        # Initialize coordination tracking if not present
        if coordination_id not in self.active_coordinations:
            self.active_coordinations[coordination_id] = {}
            self.coordination_status[coordination_id] = "active"
            logger.info(f"Started new coordination: {coordination_id}")

        # Track agents within the coordination
        if channel not in self.active_coordinations[coordination_id]:
            self.active_coordinations[coordination_id][channel] = set()

        if event_type == "agent_spawn":
            self.active_coordinations[coordination_id][channel].add(sender)
            logger.info(
                f"Coordination {coordination_id}: Agent {sender} spawned in {channel}"
            )
        elif event_type == "agent_despawn":
            if sender in self.active_coordinations[coordination_id][channel]:
                self.active_coordinations[coordination_id][channel].remove(sender)
                logger.info(
                    f"Coordination {coordination_id}: Agent {sender} despawned from {channel}"
                )

        # Check for coordination completion
        if self.coordination_status[coordination_id] == "active":
            all_agents_despawned = True
            for ch, agents in self.active_coordinations[coordination_id].items():
                if agents:  # If there are still active agents in any channel
                    all_agents_despawned = False
                    break

            if all_agents_despawned:
                self.coordination_status[coordination_id] = "complete"
                logger.info(f"Coordination {coordination_id} completed.")
                # Emit a coordination_complete event
                await self.transmit(
                    channel=channel,  # Or a dedicated system channel
                    sender="system",
                    event_type="coordination_complete",
                    coordination_id=coordination_id,
                    event_payload={"result": "Coordination finished successfully."},
                )

    async def _send(self, agent_id: str, event: Dict):
        """Send event to specific agent."""
        websocket = self.connections.get(agent_id)
        if websocket and (websocket.state == websockets.protocol.State.OPEN):
            await websocket.send(json.dumps(event))

    async def _handler(self, websocket: websockets.ServerProtocol):
        """Handle websocket connections."""
        agent_id = websocket.request.path.lstrip("/")
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
