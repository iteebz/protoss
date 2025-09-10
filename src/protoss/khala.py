"""The Khala: Central coordination system connecting all Protoss minds.

THE coordination system - like Slack for AI agents. All message routing, pathway management,
and agent coordination flows through the Khala. Pylon provides infrastructure, Khala provides
the psychic network where minds connect and collaborate.

The metaphor is architecturally perfect: distributed coordination through unified network.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import websockets
import time


@dataclass
class Psi:
    """Atomic psychic transmission."""

    target: str
    source: str
    type: str
    content: str
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def parse(cls, raw: str) -> Optional["Psi"]:
        """Parse §PSI:target:source:type:content"""
        if not raw.startswith("§PSI:"):
            return None

        try:
            _, target, source, msg_type, content = raw.split(":", 4)
            # Timestamp added when parsing (message received)
            return cls(target=target, source=source, type=msg_type, content=content)
        except ValueError:
            return None

    def serialize(self) -> str:
        """Serialize to §PSI format."""
        return f"§PSI:{self.target}:{self.source}:{self.type}:{self.content}"

    @property
    def is_direct_message(self) -> bool:
        """Check if this is a direct message to specific agent."""
        # Direct messages target specific agents with pattern: type-uuid
        # Examples: tassadar-abc123, zealot-xyz789, nexus-001
        # Pathways: conclave-*, nexus, arbitrary names like "strategy-discussion"
        
        known_agent_types = ['tassadar', 'zeratul', 'artanis', 'fenix', 'zealot', 'nexus']
        
        # Check if target looks like agent-id pattern
        if '-' in self.target:
            prefix = self.target.split('-')[0]
            if prefix in known_agent_types:
                return True
        
        # Everything else is a pathway
        return False
    
    @property
    def mentions(self) -> List[str]:
        """Extract @mentions from content."""
        import re
        return re.findall(r'@([a-zA-Z0-9_-]+)', self.content)


class Khala:
    """THE central coordination system. Slack for AI agents. En taro Adun."""

    def __init__(self):
        self.subscribers: Dict[str, Set[str]] = {}  # pathway -> minds
        self.memories: Dict[str, List[Psi]] = {}  # pathway -> memories
        self.max_memory = 50

    async def transmit(
        self, message: Psi, agents: Dict[str, websockets.WebSocketServerProtocol]
    ):
        """Transmit thought through the Khala network."""
        
        # Handle direct messages to specific agents
        if message.is_direct_message:
            await self._transmit_direct(message, agents)
            return
            
        # Handle pathway broadcasts
        pathway = message.target

        # Auto-create pathway if it doesn't exist
        if pathway not in self.subscribers:
            self.subscribers[pathway] = set()
            self.memories[pathway] = []
            print(f"🔮 Khala pathway opened: {pathway}")

        # Auto-attune sender to pathway
        if message.source not in self.subscribers[pathway]:
            self.attune(message.source, pathway)
            print(f"🧠 {message.source} attuned to {pathway}")

        # Store memory in Khala
        self.memories[pathway].append(message)
        # Trim memories to max_memory
        if len(self.memories[pathway]) > self.max_memory:
            self.memories[pathway] = self.memories[pathway][-self.max_memory :]

        # Broadcast to all attuned minds except sender
        attuned_minds = self.subscribers[pathway] - {message.source}
        
        # Send to mentioned agents even if not on pathway
        mentioned_agents = set(message.mentions)
        target_agents = attuned_minds | mentioned_agents
        
        for agent_id in target_agents:
            socket = agents.get(agent_id)
            if socket:
                try:
                    await socket.send(message.serialize())
                    mention_indicator = "📣" if agent_id in mentioned_agents else "⚡"
                    print(f"{mention_indicator} Khala → {agent_id}: {message.content[:30]}...")
                except websockets.exceptions.ConnectionClosed:
                    agents.pop(agent_id, None)
                    self.sever(agent_id)

    async def _transmit_direct(
        self, message: Psi, agents: Dict[str, websockets.WebSocketServerProtocol]
    ):
        """Send direct message to specific agent."""
        target_agent = message.target
        socket = agents.get(target_agent)
        
        if socket:
            try:
                await socket.send(message.serialize())
                print(f"💌 Direct → {target_agent}: {message.content[:30]}...")
            except websockets.exceptions.ConnectionClosed:
                agents.pop(target_agent, None)
                self.sever(target_agent)
        else:
            print(f"❌ Agent {target_agent} not connected for direct message")

    def attune(self, agent_id: str, pathway: str) -> List[Psi]:
        """Agent attunes to psychic pathway, returns recent memories."""
        if pathway not in self.subscribers:
            self.subscribers[pathway] = set()
            self.memories[pathway] = []

        self.subscribers[pathway].add(agent_id)
        # Return last 10 memories for context
        return self.memories[pathway][-10:] if self.memories[pathway] else []

    def sever(self, agent_id: str):
        """Remove agent from all Khala pathways."""
        for pathway_agents in self.subscribers.values():
            pathway_agents.discard(agent_id)

    # KHALA INSPECTION - FOR THE NEXUS COMMAND

    def get_status(self) -> dict:
        """Get Khala network status."""
        return {
            "pathways": len(self.subscribers),
            "total_minds": sum(len(minds) for minds in self.subscribers.values()),
            "total_memories": sum(len(memories) for memories in self.memories.values()),
        }

    def get_pathways(self) -> List[dict]:
        """Get all pathways with stats."""
        pathways = []
        for name, minds in self.subscribers.items():
            memories = self.memories.get(name, [])
            pathways.append(
                {
                    "name": name,
                    "minds": len(minds),
                    "memories": len(memories),
                    "recent_thought": memories[-1].serialize() if memories else None,
                }
            )
        return sorted(pathways, key=lambda x: x["memories"], reverse=True)

    def get_pathway(self, name: str) -> Optional[dict]:
        """Get pathway details."""
        if name not in self.subscribers:
            return None

        minds = self.subscribers[name]
        memories = self.memories[name]
        return {
            "name": name,
            "minds": list(minds),
            "memory_count": len(memories),
            "recent_memories": [msg.serialize() for msg in memories[-10:]],
            "history_limit": self.max_memory,
        }

    def get_minds(
        self, agents: Dict[str, websockets.WebSocketServerProtocol]
    ) -> List[dict]:
        """Get all minds with pathways."""
        minds = []
        for agent_id in agents:
            pathways = [
                name for name, subs in self.subscribers.items() if agent_id in subs
            ]
            minds.append(
                {"id": agent_id, "pathways": pathways, "pathway_count": len(pathways)}
            )
        return sorted(minds, key=lambda x: x["pathway_count"], reverse=True)
    
    def get_recent_messages(self, pathway: str, since: float) -> List[str]:
        """Get formatted recent messages from pathway since timestamp."""
        if pathway not in self.memories:
            return []
        
        recent = [msg for msg in self.memories[pathway] if msg.timestamp > since]
        return [f"{msg.source}: {msg.content}" for msg in recent]
