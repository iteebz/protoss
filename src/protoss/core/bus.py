"""Message routing and coordination for distributed agents."""

import json
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

from .server import Server
from .message import Message
from . import mentions

logger = logging.getLogger(__name__)


@dataclass
class Channel:
    """Represents a single coordination channel."""
    subscribers: Set[str] = field(default_factory=set)
    history: List[Message] = field(default_factory=list)
    task: Optional[str] = None


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

    async def transmit(self, channel: str, sender: str, content: str):
        message = Message(channel=channel, sender=sender, content=content)
        if not message.channel.startswith(("coord-", "squad-", "mission-", "channel-", "consult-")):
            await self._direct(message)
        else:
            await self._broadcast(message)

    def register(self, channel_id: str, agent_id: str):
        logger.debug(f"Agent {agent_id} attempting to register to channel {channel_id}")
        self._ensure_channel(channel_id)
        self.channels[channel_id].subscribers.add(agent_id)

    def history(self, channel_id: str, since_timestamp: float = 0) -> List[Message]:
        if channel_id not in self.channels:
            return []
        return [
            msg for msg in self.channels[channel_id].history if msg.timestamp > since_timestamp
        ]

    def deregister(self, agent_id: str):
        for channel in self.channels.values():
            channel.subscribers.discard(agent_id)

    def set_channel_task(self, channel_id: str, task: str) -> None:
        """Record canonical coordination task for a channel."""
        if task:
            self._ensure_channel(channel_id)
            self.channels[channel_id].task = task

    def get_channel_task(self, channel_id: str) -> Optional[str]:
        """Retrieve canonical coordination task for a channel if known."""
        return self.channels.get(channel_id, Channel()).task

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

    async def _handle_history_request(self, agent_id: str, data: dict):
        """Handles a request for channel history."""
        channel_id = data.get("channel")
        if not channel_id:
            logger.warning(f"History request from {agent_id} missing channel.")
            return
        
        messages = self.history(channel_id)
        history_content = [msg.content for msg in messages]
        
        response = {
            "type": "history_resp",
            "channel": channel_id,
            "history": history_content,
        }
        if self.server:
            await self.server.send(agent_id, json.dumps(response))

    async def _message(self, agent_id: str, raw_message: str):
        """Handle incoming WebSocket message from agent."""
        try:
            data = json.loads(raw_message)
            msg_type = data.get("type", "msg")
            channel = data.get("channel", "general")

            if msg_type == "status_req" and agent_id == "status_client":
                status_data = self.status()
                response = {
                    "type": "status_resp",
                    "status": "online",
                    "bus": status_data,
                }
                if self.server:
                    await self.server.send(agent_id, json.dumps(response))
                return
            
            if msg_type == "monitor_req":
                self.monitor_clients.add(agent_id)
                logger.info(f"👁️ {agent_id} is now monitoring the bus.")
                response = {"type": "monitor_ack", "status": "monitoring"}
                if self.server:
                    await self.server.send(agent_id, json.dumps(response))
                return

            if msg_type == "history_req":
                await self._handle_history_request(agent_id, data)
            elif msg_type == "join_channel":
                self.register(channel, agent_id)
                await self.transmit(channel, "system", f"🔮 {agent_id} has joined the coordination on channel {channel}")
            elif msg_type == "leave_channel":
                self.deregister(agent_id)
                await self.transmit(channel, "system", f"🔌 {agent_id} has left the coordination (departed)")
            elif msg_type == "msg":
                content = data.get("content")
                if content is None:
                    logger.warning(f"Message from {agent_id} has no content.")
                    return
                # The gateway listens on a special channel
                if channel == "gateway_commands":
                    await self.transmit(channel, agent_id, content)
                else:
                    await self.transmit(channel, agent_id, content)
            else:
                logger.warning(f"Unknown message type '{msg_type}' from {agent_id}.")

        except json.JSONDecodeError:
            logger.warning(f"Received invalid JSON from {agent_id}: {raw_message}")

    async def _connect(self, agent_id: str):
        """Handle agent connection to coordination network."""
        logger.info(f"🔮 {agent_id} connected to Khala")

    async def _disconnect(self, agent_id: str):
        """Handle agent disconnection from coordination network."""
        self.deregister(agent_id)
        self.monitor_clients.discard(agent_id)
        logger.info(f"🔌 {agent_id} disconnected from Bus")

    async def _direct(self, message: Message):
        """Send direct message to specific agent."""
        target_agent = message.channel
        logger.info(
            f"💌 DIRECT → {target_agent} ({message.sender}): {message.content[:60]}..."
        )
        if self.server:
            await self.server.send(target_agent, message.serialize())

    async def _broadcast(self, message: Message):
        """Broadcast a message to a channel and handle its side-effects."""
        self._ensure_channel(message.channel)

        self._append_to_history(message)
        await self._persist_message(message)

        logger.info(f"⚡ MESSAGE → {message.channel} ({message.sender}): {message.content[:60]}...")

        await self._send_to_subscribers(message)

    async def _send_to_subscribers(self, message: Message):
        """Send the message to all agents subscribed to the channel and all monitors."""
        if not self.server:
            return

        broadcast_payload = {
            "type": "msg",
            "sender": message.sender,
            "content": message.content,
            "channel": message.channel,
        }
        json_payload = json.dumps(broadcast_payload)
        
        subscribers = self.channels.get(message.channel, Channel()).subscribers
        targets = subscribers | set(mentions.extract_mentions(message.content)) | self.monitor_clients

        for agent_id in targets:
            if agent_id == message.sender:
                continue
            await self.server.send(agent_id, json_payload)

    def is_running(self) -> bool:
        """Check if the Bus server is currently running."""
        return self.server is not None and self.server.is_running()

# Pure dependency injection - no global state
# Applications must create and manage their own Bus instances
