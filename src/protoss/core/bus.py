"""A simple, unified message bus for agent coordination."""

import asyncio
import json
import logging
import socket
import time
from typing import Any, Dict, Set, Optional, List
from dataclasses import dataclass, field

import websockets
from .message import Message
from . import parser
from .protocols import Mention, BaseSignal
from . import gateway
from .protocols import Storage
from protoss.lib.storage import SQLite

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


@dataclass
class Event:
    """Canonical coordination event flowing through the Bus."""

    type: str
    channel: str
    sender: str
    timestamp: float
    payload: Dict[str, Any]
    message: Message
    coordination_id: Optional[str] = None
    content: str = ""
    signals: List[BaseSignal] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to the canonical wire format."""
        event_dict = {
            "type": self.type,
            "channel": self.channel,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "coordination_id": self.coordination_id,
            "content": self.content,
            "payload": self.payload,
            "signals": [signal.to_dict() for signal in self.signals],
            "message": self.message.to_dict(),
        }

        if self.coordination_id is None:
            event_dict.pop("coordination_id")
        return event_dict


# ==============================================================================
# The Purified Bus Facade
# ==============================================================================


class Bus:
    """A single facade for message routing and coordination.
    Responsibilities are owned explicitly inside the facade."""

    def __init__(
        self,
        port: int = 8888,
        max_agents: int = 100,
        storage_path: Optional[str] = None,
    ):
        self.port = port
        self.max_agents = max_agents
        self.server: Optional[websockets.WebSocketServer] = None
        self.storage: Storage = SQLite(storage_path or "./.protoss/store.db")

        # State owned by the Bus coordinator
        self.connections: Dict[str, websockets.ServerProtocol] = {}
        self.channels: Dict[str, Channel] = {}  # Channel state with history
        self.active_agents: Dict[str, Set[str]] = {}  # channel -> agent_ids
        self.coordinations: Dict[str, Coordination] = {}

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
        """Creates, records, and broadcasts a canonical event."""
        coordination_id = kwargs.pop("coordination_id", None)
        payload = kwargs.pop("event_payload", None)
        if payload is None:
            payload = kwargs.pop("payload", None)
        payload = dict(payload or {})

        content = kwargs.pop("content", None)
        if content is None:
            content = payload.get("content", "")
        elif content and "content" not in payload:
            payload = {**payload, "content": content}

        signals = parser.signals(content) if content else []
        message_obj = Message(
            channel=channel,
            sender=sender,
            event=payload,
            msg_type=event_type,
            coordination_id=coordination_id,
        )
        message_obj.signals = signals

        event = Event(
            type=event_type,
            channel=channel,
            sender=sender,
            timestamp=message_obj.timestamp,
            payload=payload,
            message=message_obj,
            coordination_id=coordination_id,
            content=content,
            signals=signals,
        )

        channel_state = self.channels.setdefault(channel, Channel())
        channel_state.history.append(message_obj)

        await self._persist_event(event)
        await self._update_lifecycle(event)

        if event.type in {"agent_message", "vision_seed"}:
            await self._dispatch_mentions(event)
        if event.type == "agent_message":
            await self._handle_probe_command(event)

        await self._broadcast_event(event)

    async def _persist_event(self, event: Event) -> None:
        """Persist the event, logging any failure."""
        try:
            await self.storage.save_event(event.to_dict())
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("❌ Failed to save event: %s", exc, exc_info=True)

    async def _dispatch_mentions(self, event: Event) -> None:
        """Spawn agents based on @mentions in the event content."""
        for signal in event.signals:
            if not isinstance(signal, Mention) or signal.agent_name == "probe":
                continue

            agent_type = signal.agent_name
            channel = event.channel
            if not gateway.should_spawn(
                agent_type, channel, self.active_agents, self.max_agents
            ):
                continue

            try:
                bus_url = self.url
                spawn_coro = gateway.spawn_agent(agent_type, channel, bus_url)

                async def _complete_spawn():
                    try:
                        await spawn_coro
                        logger.info(
                            "Spawning %s for @mention in %s", agent_type, channel
                        )
                        await self.transmit(
                            channel=channel,
                            sender="system",
                            event_type="agent_spawn",
                            coordination_id=event.coordination_id,
                            event_payload={
                                "agent_type": agent_type,
                                "spawned_by": event.sender,
                            },
                        )
                    except Exception as spawn_error:  # pragma: no cover
                        logger.error(
                            "Failed to spawn %s: %s", agent_type, spawn_error,
                            exc_info=True,
                        )

                asyncio.create_task(_complete_spawn())
            except Exception as exc:  # pragma: no cover
                logger.error("Failed to spawn %s: %s", agent_type, exc, exc_info=True)

    async def _handle_probe_command(self, event: Event) -> None:
        """Execute probe commands emitted via @probe mention."""
        if event.type != "agent_message":
            return

        for signal in event.signals:
            if isinstance(signal, Mention) and signal.agent_name == "probe":
                command_str = event.payload.get("content", event.content)
                if not command_str:
                    return
                try:
                    command = json.loads(command_str)
                except (json.JSONDecodeError, ValueError) as exc:
                    logger.error("Error handling probe command: %s", exc)
                    return

                action = command.get("action")
                if action == "create_channel":
                    await self._probe_create_channel(command, event.coordination_id)
                else:
                    logger.error("Unknown probe action: %s", action)
                return

    async def _probe_create_channel(
        self, command: Dict[str, Any], coordination_id: Optional[str]
    ) -> None:
        import re
        from uuid import uuid4

        description = command.get("description")
        instruction = command.get("instruction")
        if not description:
            raise ValueError("Probe 'create_channel' missing 'description'.")

        channel_slug = re.sub(r"[\s_]+", "-", description.lower()).strip("-")
        new_channel_id = f"task:{channel_slug}-{uuid4().hex[:8]}:active"

        logger.info("Probe creating new channel: %s", new_channel_id)
        if instruction:
            await self.transmit(
                channel=new_channel_id,
                sender="system",
                event_type="agent_message",
                coordination_id=coordination_id,
                event_payload={"content": instruction},
            )

    def _coordination_agent_label(self, event: Event) -> Optional[str]:
        return (
            event.payload.get("agent_type")
            or event.payload.get("agent_id")
            or event.sender
        )

    async def _update_lifecycle(self, event: Event) -> None:
        """Track coordination lifecycle and emit completion when appropriate."""
        coordination_id = event.coordination_id
        if not coordination_id:
            return

        coordination = self.coordinations.setdefault(coordination_id, Coordination())
        coordination.channels.setdefault(event.channel, set())

        if event.type == "coordination_complete":
            coordination.status = "complete"
            return

        if coordination.status == "complete":
            return

        agent_label = self._coordination_agent_label(event)

        if event.type == "agent_spawn":
            if agent_label:
                coordination.add_agent(event.channel, agent_label)
            return

        if event.type == "agent_despawn" and agent_label:
            coordination.remove_agent(event.channel, agent_label)

        if coordination.had_agents and coordination.is_empty():
            await self._emit_coordination_complete(coordination_id, event.channel)

    async def _emit_coordination_complete(
        self, coordination_id: str, channel: str
    ) -> None:
        coordination = self.coordinations.setdefault(coordination_id, Coordination())
        if coordination.status == "complete":
            return

        coordination.status = "complete"
        logger.info("Coordination %s completed.", coordination_id)
        await self.transmit(
            channel=channel,
            sender="system",
            event_type="coordination_complete",
            coordination_id=coordination_id,
            event_payload={"result": "Coordination finished successfully."},
        )

    async def _send_history(
        self,
        websocket: websockets.ServerProtocol,
        channel: str,
        since: Optional[float] = None,
    ):
        """Respond to history requests with persisted events."""
        history = await self.get_events(channel=channel, since=since)
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
        return await self.storage.load_events(channel=channel, since=since)

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
                if event_type == "history_req":
                    await self._send_history(websocket, channel, data.get("since"))
                    continue

                self.register(channel, agent_id)

                payload = data.get("payload") or {"content": data.get("content", "")}
                await self.transmit(
                    channel=channel,
                    sender=agent_id,
                    event_type=event_type,
                    coordination_id=data.get("coordination_id"),
                    content=data.get("content"),
                    payload=payload,
                )

        except websockets.ConnectionClosed:
            pass
        finally:
            self.connections.pop(agent_id, None)
            for agents in self.active_agents.values():
                agents.discard(agent_id)
            logger.info(f"🔌 {agent_id} disconnected")

    async def _broadcast_event(self, event: Event):
        """Broadcast the canonical event to channel subscribers."""
        wire_event = event.to_dict()
        channel = wire_event.get("channel", "")
        sender = wire_event.get("sender", "")
        subscribers = self.active_agents.get(channel, set())

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
        if channel not in self.active_agents:
            self.active_agents[channel] = set()

        self.channels[channel].subscribers.add(agent_id)
        self.active_agents[channel].add(agent_id)

    def deregister(self, agent_id: str):
        """Deregister agent from all channels."""
        for channel_agents in self.active_agents.values():
            channel_agents.discard(agent_id)
        for channel in self.channels.values():
            channel.subscribers.discard(agent_id)

    async def _broadcast(self, message: Message):
        """Legacy broadcast method for tests."""
        payload = message.event or {}
        content = payload.get("content", "")
        event = Event(
            type="agent_message",
            channel=message.channel,
            sender=message.sender,
            timestamp=message.timestamp,
            payload=payload,
            message=message,
            coordination_id=message.coordination_id,
            content=content,
            signals=message.signals,
        )

        # Ensure channel exists and store message
        if message.channel not in self.channels:
            self.channels[message.channel] = Channel()
        self.channels[message.channel].history.append(message)

        await self._broadcast_event(event)


def main():
    """Entry point for running the Bus as a standalone process."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the Protoss Bus.")
    parser.add_argument("--port", type=int, default=8888, help="Port to run on")
    parser.add_argument(
        "--max-agents", type=int, default=100, help="Max agents per channel"
    )
    parser.add_argument(
        "--storage-path", type=str, help="Path to SQLite database file."
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
        logger.info("Bus shutting down.")
        loop.run_until_complete(bus.stop())


if __name__ == "__main__":
    main()
