"""Message routing and coordination for distributed agents."""

from typing import Dict, List, Set, Optional
from .server import Server
from .spawner import Spawner
from .message import Message


class Bus:
    """Message routing and coordination for distributed agents."""

    def __init__(
        self,
        port: int = None,
        max_memory: int = 50,
        storage=None,
        spawner=None,
        max_agents: Optional[int] = None,
        enable_storage: bool = True,
        storage_base_dir: Optional[str] = None,
    ):
        """Initialize Bus coordination system.

        Args:
            port: WebSocket server port (default 8888)
            max_memory: Maximum messages to retain per channel
            storage: Optional storage backend for persistence
            mention_handlers: Dict of mention handlers (e.g. {"archon": archon_instance})
            spawner: Spawner instance for adaptive agent management
        """
        self.server: Optional[Server] = None
        self.channels: Dict[str, Set[str]] = {}
        self.memories: Dict[str, List[Message]] = {}
        self.max_memory = max_memory
        self.port = port or 8888
        self.storage = self._init_storage(storage, enable_storage, storage_base_dir)

        # Adaptive spawning
        max_agents_per_channel = max_agents if max_agents is not None else 10
        self.spawner = spawner or Spawner(max_agents_per_channel=max_agents_per_channel)

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
        except Exception as exc:  # pragma: no cover - fallback to in-memory
            print(
                f"⚠️ Storage initialization failed ({exc}); continuing without persistence"
            )
            return None

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

        # Handle @mention escalations via Spawner
        await self.spawner.handle_mention(message, self)

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

    async def spawn(
        self, agent_ref: str, channel_id: str, context: str = "Manual spawn"
    ) -> bool:
        """Universal agent participation - spawn fresh or reactivate existing.

        Args:
            agent_ref: Agent reference - either type ("zealot") or specific ID ("zealot-abc123")
            channel_id: Channel for agent participation
            context: Context message for spawning

        Returns:
            True if spawn/reactivation was successful, False if failed
        """
        trigger_message = Message(channel=channel_id, sender="system", content=context)

        if self.spawner._is_specific_agent_mention(agent_ref):
            return await self.spawner._respawn(
                agent_ref, channel_id, trigger_message, self
            )

        return await self.spawner._spawn(agent_ref, channel_id, trigger_message, self)

    async def despawn(self, agent_id: str) -> bool:
        """Handle agent despawn via Spawner."""
        result = await self.spawner.despawn_agent(agent_id)
        if result:
            self.sever(agent_id)
        return result

    def get_team_status(self, channel_id: str) -> str:
        """Get team status for agent awareness via Spawner."""
        return self.spawner.get_team_status(channel_id)


# Pure dependency injection - no global state
# Applications must create and manage their own Bus instances
