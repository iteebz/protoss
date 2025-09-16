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

    pathway: str
    sender: str
    content: str
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def parse(cls, raw: str) -> Optional["Psi"]:
        """Parse §PSI|pathway|sender: message"""
        if not raw.startswith("§PSI|"):
            return None

        try:
            # Split protocol parts: §PSI|pathway|sender: content
            parts = raw[5:].split("|", 2)  # Remove "§PSI|" prefix
            if len(parts) != 2:
                return None
                
            pathway = parts[0]
            sender_content = parts[1]
            
            # Split sender and content on first colon+space
            if ": " in sender_content:
                sender, content = sender_content.split(": ", 1)
            else:
                # Fallback if no colon separator
                sender, content = sender_content, ""
                
            return cls(pathway=pathway, sender=sender, content=content)
        except ValueError:
            return None

    def serialize(self) -> str:
        """Serialize to §PSI format."""
        return f"§PSI|{self.pathway}|{self.sender}: {self.content}"

    @property
    def is_direct_message(self) -> bool:
        """Check if this is a direct message to specific agent."""
        # Direct messages target specific agents with pattern: type-uuid
        # Examples: tassadar-abc123, zealot-xyz789, nexus-001
        # Pathways: conclave-*, nexus, arbitrary names like "strategy-discussion"
        
        known_agent_types = ['tassadar', 'zeratul', 'artanis', 'fenix', 'zealot', 'nexus']
        
        # Check if pathway looks like agent-id pattern
        if '-' in self.pathway:
            prefix = self.pathway.split('-')[0]
            if prefix in known_agent_types:
                return True
        
        # Everything else is a group pathway
        return False
    
    @property
    def mentions(self) -> List[str]:
        """Extract @mentions from content."""
        import re
        return re.findall(r'@([a-zA-Z0-9_-]+)', self.content)


class KhalaConnection:
    """Individual agent connection to Khala network."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.connection = None
        
    async def __aenter__(self):
        """Connect to Khala network."""
        connection_uri = f"{khala.get_grid_uri()}/{self.agent_id}"
        self.connection = await websockets.connect(connection_uri)
        print(f"🔹 {self.agent_id} connected to Khala network")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Disconnect from Khala network."""
        if self.connection:
            await self.connection.close()
            print(f"🔌 {self.agent_id} disconnected from Khala")
            
    async def send(self, pathway: str, content: str):
        """Send psi message to pathway."""
        psi = Psi(pathway=pathway, sender=self.agent_id, content=content)
        await self.connection.send(psi.serialize())
        
    async def receive(self):
        """Receive psi message."""
        try:
            raw_message = await self.connection.recv()
            return Psi.parse(raw_message)
        except websockets.exceptions.ConnectionClosed:
            return None


class Khala:
    """Khala implementation - singleton consciousness substrate."""
    
    def __init__(self):
        self.subscribers = {}  # pathway -> minds
        self.memories = {}  # pathway -> memories  
        self.agents = {}  # agent_id -> websocket connection
        self.max_memory = 50
        self._grid_port = None
        
        # Background persistence
        from .forge import SQLite
        self.storage: "Storage" = SQLite()

    def set_grid_port(self, port: int):
        """Set the active Pylon grid port."""
        self._grid_port = port
        
    def get_grid_port(self) -> int:
        """Get the active Pylon grid port."""
        from .constants import PYLON_DEFAULT_PORT
        return self._grid_port or PYLON_DEFAULT_PORT
        
    def get_grid_uri(self) -> str:
        """Get the active Pylon grid WebSocket URI."""
        from .constants import pylon_uri
        return pylon_uri("localhost", self.get_grid_port())
        
    def connect(self, agent_id: str):
        """Connect agent to Khala network."""
        return KhalaConnection(agent_id)

    async def transmit(self, pathway: str = None, sender: str = None, content: str = None, psi: Psi = None):
        """Stream consciousness to pathway - canonical coordination interface."""
        if psi is None:
            psi = Psi(pathway=pathway, sender=sender, content=content)
        
        # Handle direct messages to specific agents
        if psi.is_direct_message:
            target_agent = psi.pathway
            
            # LOCAL MODE: Just log the direct message
            print(f"💌 DIRECT → {target_agent} ({psi.sender}): {psi.content[:60]}...")
            
            # WebSocket mode (if connected)
            socket = self.agents.get(target_agent)
            if socket:
                try:
                    await socket.send(psi.serialize())
                    print(f"💌 WebSocket → {target_agent}: {psi.content[:30]}...")
                except websockets.exceptions.ConnectionClosed:
                    self.agents.pop(target_agent, None)
                    self.sever(target_agent)
            return
            
        # Handle pathway broadcasts
        pathway = psi.pathway

        # Auto-create pathway if it doesn't exist
        if pathway not in self.subscribers:
            self.subscribers[pathway] = set()
            self.memories[pathway] = []
            print(f"🔮 Khala pathway opened: {pathway}")

        # Store memory in Khala
        self.memories[pathway].append(psi)
        # Trim memories to max_memory
        if len(self.memories[pathway]) > self.max_memory:
            self.memories[pathway] = self.memories[pathway][-self.max_memory :]

        # Background persistence to forge
        import asyncio
        asyncio.create_task(self.storage.save_psi(pathway, psi.sender, psi.content, psi.timestamp))

        # LOCAL MODE: Just log the transmission for now
        print(f"⚡ PSI → {pathway} ({psi.sender}): {psi.content[:60]}...")
        
        # Broadcast to all attuned minds (WebSocket mode)
        attuned_minds = self.subscribers.get(pathway, set())
        
        # Send to mentioned agents even if not on pathway
        mentioned_agents = set(psi.mentions)
        target_agents = attuned_minds | mentioned_agents
        
        for agent_id in target_agents:
            socket = self.agents.get(agent_id)
            if socket:
                try:
                    await socket.send(psi.serialize())
                    mention_indicator = "📣" if agent_id in mentioned_agents else "⚡"
                    print(f"{mention_indicator} Khala → {agent_id}: {psi.content[:30]}...")
                except websockets.exceptions.ConnectionClosed:
                    self.agents.pop(agent_id, None)
                    self.sever(agent_id)

    def attune(self, pathway: str, since_timestamp: float = 0) -> List[Psi]:
        """Absorb consciousness streams from pathway since timestamp."""
        if pathway not in self.memories:
            return []
            
        # Return messages since timestamp for coordination awareness
        return [
            msg for msg in self.memories[pathway] 
            if msg.timestamp > since_timestamp
        ]

    def register_agent(self, agent_id: str, websocket):
        """Register agent connection with Khala."""
        self.agents[agent_id] = websocket
        print(f"🔹 {agent_id} registered with Khala")
        
    def sever(self, agent_id: str):
        """Remove agent from all Khala pathways."""
        for pathway_agents in self.subscribers.values():
            pathway_agents.discard(agent_id)
        self.agents.pop(agent_id, None)

    # KHALA INSPECTION - FOR THE NEXUS COMMAND

    @property
    def status(self) -> dict:
        """Khala network status."""
        return {
            "pathways": len(self.subscribers),
            "total_minds": sum(len(minds) for minds in self.subscribers.values()),
            "total_memories": sum(len(memories) for memories in self.memories.values()),
        }

    async def pathways(self) -> List[dict]:
        """All pathways with stats (combines memory + persistent data)."""
        # Get persistent pathways from storage
        persistent_pathways = await self.storage.load_pathways()
        
        # Merge with in-memory pathways
        pathways = {}
        
        # Add persistent pathways
        for p in persistent_pathways:
            pathways[p["name"]] = {
                "name": p["name"],
                "minds": 0,  # Will update from memory
                "memories": p["message_count"],
                "recent_thought": None,  # Will update from memory
            }
        
        # Update with in-memory data
        for name, minds in self.subscribers.items():
            if name not in pathways:
                pathways[name] = {"name": name, "minds": 0, "memories": 0, "recent_thought": None}
            
            pathways[name]["minds"] = len(minds)
            memories = self.memories.get(name, [])
            pathways[name]["recent_thought"] = memories[-1].serialize() if memories else None
            
        return sorted(pathways.values(), key=lambda x: x["memories"], reverse=True)

    def pathway(self, name: str) -> Optional[dict]:
        """Pathway details."""
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

    @property 
    def minds(self) -> List[dict]:
        """All minds with pathways."""
        minds = []
        for agent_id in self.agents:
            pathways = [
                name for name, subs in self.subscribers.items() if agent_id in subs
            ]
            minds.append(
                {"id": agent_id, "pathways": pathways, "pathway_count": len(pathways)}
            )
        return sorted(minds, key=lambda x: x["pathway_count"], reverse=True)
    
    async def recent_messages(self, pathway: str, since: float = 0) -> List[str]:
        """Recent messages from pathway since timestamp."""
        # Try in-memory first (hot data)
        if pathway in self.memories:
            recent = [msg for msg in self.memories[pathway] if msg.timestamp > since]
            if recent:
                return [msg.content for msg in recent]
        
        # Fallback to persistent storage (cold data)
        return await self.storage.get_recent_messages(pathway, limit=10)


# Module-level singleton - clean and direct
khala = Khala()
