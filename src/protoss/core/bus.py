import asyncio
import json
import logging
import socket
import time
from collections import defaultdict
from typing import Dict, Set, Optional, List, AsyncIterator, Tuple
from dataclasses import dataclass, field

import websockets
from .event import Event
from . import parser
from . import gateway
from .protocols import Storage, Mention
from protoss.lib.storage import SQLite
from protoss.tools import probe

logger = logging.getLogger(__name__)


@dataclass
class Channel:
    """Channel state with history and subscribers."""

    history: List[Event] = field(default_factory=list)
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
        port: int = 8888,
        storage_path: Optional[str] = None,
        max_units: int = 100,
    ):
        self.port = port
        self.server: Optional[websockets.WebSocketServer] = None
        self.storage: Storage = SQLite(storage_path or "./.protoss/store.db")
        self.max_units = max_units

        # State owned by the Bus facade
        self.connections: Dict[str, websockets.ServerProtocol] = {}
        self.channels: Dict[str, Channel] = {}  # Channel state with history

        # Nexus functionality merged into Bus
        self._subscribers: Dict[
            Optional[str], List[Tuple[asyncio.Queue, Optional[str]]]
        ] = defaultdict(list)
        self._general_subscribers: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()

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

    async def publish(self, event: Event):
        """
        Publishes an event to all relevant subscribers (internal and external).
        """
        if not isinstance(event, Event):
            logger.error(f"Attempted to publish non-Event object: {type(event)}")
            return

        # Publish to internal general subscribers
        for queue in self._general_subscribers:
            await queue.put(event)

        # Publish to internal type-specific subscribers
        if event.type in self._subscribers:
            for queue, filter_channel in self._subscribers[event.type]:
                if filter_channel is None or filter_channel == event.channel:
                    await queue.put(event)

        # Broadcast to external WebSocket subscribers
        await self._broadcast_event(event)

        logger.debug(f"Published event: {event.type} to channel {event.channel}")

    async def subscribe(
        self, event_type: Optional[str] = None, channel: Optional[str] = None
    ) -> AsyncIterator[Event]:
        """
        Subscribes to events.
        If event_type is None, subscribes to all events.
        If channel is not None, filters events by channel for type-specific subscriptions.
        """
        queue = asyncio.Queue()
        async with self._lock:
            if event_type is None:
                self._general_subscribers.append(queue)
            else:
                self._subscribers[event_type].append((queue, channel))

        logger.debug(f"New subscriber for event_type={event_type}, channel={channel}")

        try:
            while True:
                yield await queue.get()
        except asyncio.CancelledError:
            logger.debug(
                f"Subscriber cancelled for event_type={event_type}, channel={channel}"
            )
        finally:
            async with self._lock:
                if event_type is None:
                    if queue in self._general_subscribers:
                        self._general_subscribers.remove(queue)
                else:
                    if (queue, channel) in self._subscribers[event_type]:
                        self._subscribers[event_type].remove((queue, channel))

    async def transmit(self, channel: str, sender: str, event_type: str, **kwargs):
        """Creates a canonical Event, persists it, and publishes it."""
        coordination_id = kwargs.pop("coordination_id", None)
        payload = kwargs.pop("event_payload", None) or kwargs.pop("payload", None) or {}
        content = kwargs.pop("content", None) or payload.get("content", "")

        signals = parser.signals(content) if content else []

        event = Event(
            type=event_type,
            channel=channel,
            sender=sender,
            payload=payload,
            coordination_id=coordination_id,
            content=content,
            signals=signals,
        )

        channel_state = self.channels.setdefault(channel, Channel())
        channel_state.history.append(event)

        # Persist the event directly, absorbing the Archiver's role.
        try:
            await self.storage.save_event(event.to_dict())
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to persist event: %s", exc)

        # Absorb Observer role: check for mentions and spawn units
        await self._handle_mentions(event)

        await self.publish(event)

    async def _handle_mentions(self, event: Event):
        """Processes an event to detect @mentions and trigger actions."""
        if not event.signals:
            return

        for signal in event.signals:
            if not isinstance(signal, Mention):
                continue

            agent_type = signal.agent_name
            channel = event.channel

            # Handle @probe as an internal Bus function
            if agent_type == "probe":
                await self._execute_probe_tool(event)
                continue

            # Get active units for the channel
            active_units_in_channel = self.channels.get(channel, Channel()).subscribers
            active_units_snapshot = {channel: set(active_units_in_channel)}

            if not gateway.should_spawn_agent(
                agent_type, channel, active_units_snapshot, self.max_units
            ):
                continue

            await self._spawn_agent_and_publish_event(agent_type, channel, event)

    async def _execute_probe_tool(self, event: Event):
        """Executes the probe tool with the given event."""
        await probe.execute(event, self)

    async def _spawn_agent_and_publish_event(
        self, agent_type: str, channel: str, original_event: Event
    ):
        """Spawns an agent and publishes an agent_spawn event."""
        try:
            await gateway.spawn_agent(agent_type, channel, self.url)
            logger.info("Bus: Spawning %s for @mention in %s", agent_type, channel)

            await self.publish(
                Event(
                    type="agent_spawn",
                    channel=channel,
                    sender="system",
                    coordination_id=original_event.coordination_id,
                    payload={
                        "agent_type": agent_type,
                        "spawned_by": original_event.sender,
                    },
                )
            )
        except Exception as exc:
            logger.error("Bus: Failed to spawn %s: %s", agent_type, exc, exc_info=True)

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
            self.deregister(agent_id)
            logger.info(f"🔌 {agent_id} disconnected")

    async def _broadcast_event(self, event: Event):
        """Broadcast the canonical event to channel subscribers."""
        wire_event = event.to_dict()
        channel = wire_event.get("channel", "")
        sender = wire_event.get("sender", "")
        subscribers = self.channels.get(channel, Channel()).subscribers

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
        for channel_state in self.channels.values():
            channel_state.subscribers.discard(agent_id)

    async def _send_history(
        self,
        websocket: websockets.ServerProtocol,
        channel: str,
        since: Optional[float] = None,
    ):
        """Respond to history requests with persisted events."""
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

    bus = Bus(port=args.port, storage_path=args.storage_path)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bus.start())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Bus shutting down.")
        loop.run_until_complete(bus.stop())


if __name__ == "__main__":
    main()
