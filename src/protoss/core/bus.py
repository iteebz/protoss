"""Message routing and coordination for distributed agents."""

import time
from typing import Dict, List, Set, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from .server import Server

if TYPE_CHECKING:
    from typing import Protocol

    class MentionHandler(Protocol):
        async def respond_to_mention(
            self, mention_context: str, channel_id: str
        ) -> str: ...


@dataclass
class Message:
    """Message for agent coordination."""

    channel: str  # Target channel or agent_id for direct messages
    sender: str  # Agent ID that created this message
    content: str  # Message content with potential @mentions
    timestamp: float = field(default_factory=time.time)  # Unix timestamp

    def serialize(self) -> str:
        """Serialize for transmission."""
        return self.content

    @property
    def is_direct_message(self) -> bool:
        """Check if this is a direct message (channel = agent_id)."""
        # Direct messages target specific agent IDs, not coordination channels
        # Coordination channels: coord-, squad-, mission-, channel-, consult-
        return not self.channel.startswith(
            ("coord-", "squad-", "mission-", "channel-", "consult-")
        )

    @property
    def mentions(self) -> List[str]:
        """Extract @mentions from content."""
        import re

        return re.findall(r"@(\w+)", self.content)


# Psi is dead, we use Message now


class Bus:
    """Message routing and coordination for distributed agents."""

    def __init__(
        self,
        port: int = None,
        max_memory: int = 50,
        storage=None,
        mention_handlers=None,
    ):
        """Initialize Bus coordination system.

        Args:
            port: WebSocket server port (default 8888)
            max_memory: Maximum messages to retain per channel
            storage: Optional storage backend for persistence
            mention_handlers: Dict of mention handlers (e.g. {"archon": archon_instance})
        """
        self.server: Optional[Server] = None
        self.channels: Dict[str, Set[str]] = {}
        self.memories: Dict[str, List[Message]] = {}
        self.max_memory = max_memory
        self.mention_handlers: Dict[str, "MentionHandler"] = mention_handlers or {}
        self.port = port or 8888
        self.storage = storage

    async def start(self):
        if self.server is None:
            self.server = Server(self.port)
            self.server.on_message(self._message)
            self.server.on_connect(self._connect)
            self.server.on_disconnect(self._disconnect)
            await self.server.start()
            print("🔮 Bus coordination network online")

    async def stop(self):
        if self.server:
            await self.server.stop()
            self.server = None

    async def transmit(self, channel: str, sender: str, content: str):
        message = Message(channel=channel, sender=sender, content=content)

        # Handle direct messages
        if message.is_direct_message:
            await self._direct(message)
            return

        # Handle channel broadcasts
        await self._broadcast(message)

    def register(self, channel: str, agent_id: str):
        self._ensure_channel(channel)
        self.channels[channel].add(agent_id)

    def history(self, channel: str, since_timestamp: float = 0) -> List[Message]:
        if channel not in self.memories:
            return []
        return [
            msg for msg in self.memories[channel] if msg.timestamp > since_timestamp
        ]

    def get_history(self, channel: str, since_timestamp: float = 0) -> List[Message]:
        """Backward compatible alias for legacy code paths."""
        return self.history(channel, since_timestamp)

    def sever(self, agent_id: str):
        for channel_agents in self.channels.values():
            channel_agents.discard(agent_id)

    def status(self) -> dict:
        return {
            "channels": len(self.channels),
            "agents": sum(len(agents) for agents in self.channels.values()),
            "memories": sum(len(memories) for memories in self.memories.values()),
        }

    async def channels_list(self) -> List[dict]:
        result = []
        for name, agents in self.channels.items():
            memories = self.memories.get(name, [])
            result.append(
                {
                    "name": name,
                    "agents": len(agents),
                    "memories": len(memories),
                    "recent": memories[-1].content if memories else None,
                }
            )
        return sorted(result, key=lambda x: x["memories"], reverse=True)

    async def recent(self, channel: str, limit: int = 10) -> List[str]:
        memories = self.memories.get(channel, [])
        return [msg.content for msg in memories[-limit:]]

    def _ensure_channel(self, channel: str):
        """Guarantee channel bookkeeping exists."""
        if channel not in self.channels:
            self.channels[channel] = set()
            self.memories[channel] = []
            print(f"🔮 Bus channel opened: {channel}")

    async def _message(self, agent_id: str, raw_message: str):
        """Handle incoming WebSocket message from agent."""
        # Parse message for channel routing
        # Format: "channel:content" or just "content" for default
        if ":" in raw_message and not raw_message.startswith("http"):
            channel, content = raw_message.split(":", 1)
            channel = channel.strip()
            content = content.strip()
        else:
            channel = "general"  # Default channel
            content = raw_message

        # Route message through normal transmission
        await self.transmit(channel, agent_id, content)

    async def _connect(self, agent_id: str):
        """Handle agent connection to coordination network."""
        print(f"🔮 {agent_id} connected to Khala")
        await self._send_memories(agent_id)

    async def _disconnect(self, agent_id: str):
        """Handle agent disconnection from coordination network."""
        self.sever(agent_id)
        print(f"🔌 {agent_id} disconnected from Bus")

    async def _send_memories(self, agent_id: str):
        """Send recent memories to reconnecting agent."""
        if not self.server:
            return

        for channel_name, agents in self.channels.items():
            if agent_id in agents:
                memories = self.history(channel_name, since_timestamp=0)
                for message in memories:
                    await self.server.send(agent_id, message.content)

    async def _direct(self, message: Message):
        """Send direct message to specific agent."""
        target_agent = message.channel
        print(
            f"💌 DIRECT → {target_agent} ({message.sender}): {message.content[:60]}..."
        )

        if self.server:
            await self.server.send(target_agent, message.serialize())

    async def _broadcast(self, message: Message):
        """Send broadcast message to channel subscribers."""
        channel = message.channel

        # Auto-create channel if needed
        self._ensure_channel(channel)

        # Store memory
        self.memories[channel].append(message)
        if len(self.memories[channel]) > self.max_memory:
            self.memories[channel] = self.memories[channel][-self.max_memory :]

        # Save to persistent storage
        await self._save(message)

        print(f"⚡ MESSAGE → {channel} ({message.sender}): {message.content[:60]}...")

        # Handle @mention escalations
        for mention in message.mentions:
            if mention in self.mention_handlers:
                await self._handle_mention(message, mention)

        # Send to channel subscribers + mentioned agents
        targets = self.channels.get(channel, set()) | set(message.mentions)
        if self.server:
            for agent_id in targets:
                await self.server.send(agent_id, message.content)

    async def _save(self, message: Message):
        """Save message to persistent storage if configured."""
        if self.storage:
            try:
                await self.storage.save_message(
                    message.channel, message.sender, message.content, message.timestamp
                )
            except Exception as e:
                print(f"⚠️ Storage error: {e}")

    async def _handle_mention(self, message: Message, mention: str):
        """Handle @mention escalation through direct dependency injection."""
        channel = message.channel
        handler = self.mention_handlers.get(mention)

        if handler is None:
            await self.transmit(channel, "system", f"@{mention} handler not available")
            return

        # Build brief context window for the mention
        recent = self.history(channel)
        context_lines = [f"{msg.sender}: {msg.content}" for msg in recent[-5:]]
        mention_context = "\n".join(context_lines) if context_lines else message.content

        # Get handler response
        try:
            response = await handler.respond_to_mention(mention_context, channel)
            handler_id = getattr(handler, "id", mention)
            await self.transmit(channel, handler_id, response)
        except Exception as e:
            await self.transmit(channel, mention, f"[{mention} error: {e}]")


# Pure dependency injection - no global state
# Applications must create and manage their own Bus instances
