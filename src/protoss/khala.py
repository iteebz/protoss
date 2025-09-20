"""Khala: Pure coordination functions.

Clean functions for PSI transmission and pathway management.
"""

import asyncio
import time
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from .structures.pylon import Pylon
from .constants import PYLON_DEFAULT_PORT

# Global coordination state
_pylon: Optional[Pylon] = None
_pathways: Dict[str, Set[str]] = {}
_memories: Dict[str, List['Psi']] = {}
_max_memory = 50


@dataclass
class Psi:
    """PSI protocol message."""
    pathway: str
    sender: str
    content: str
    timestamp: float = field(default_factory=time.time)


    def serialize(self) -> str:
        """Serialize for transmission."""
        return self.content

    @property
    def is_direct_message(self) -> bool:
        """Check if this is a direct message (pathway = agent_id)."""
        return not self.pathway.startswith(("squad-", "mission-", "pathway-"))

    @property
    def mentions(self) -> List[str]:
        """Extract @mentions from content."""
        import re
        return re.findall(r'@(\w+)', self.content)


async def start(port: int = None):
    """Start Khala coordination system."""
    global _pylon
    
    if _pylon is None:
        _pylon = Pylon(port or PYLON_DEFAULT_PORT)
        _pylon.on_message(_message)
        _pylon.on_connect(_connect)
        _pylon.on_disconnect(_disconnect)
        await _pylon.start()
        print("🔮 Khala coordination network online")


async def stop():
    """Stop Khala coordination system."""
    global _pylon
    if _pylon:
        await _pylon.stop()
        _pylon = None


async def transmit(pathway: str, sender: str, content: str):
    """Send message through the network."""
    psi = Psi(pathway=pathway, sender=sender, content=content)

    # Handle direct messages
    if psi.is_direct_message:
        await _direct(psi)
        return

    # Handle pathway broadcasts
    await _broadcast(psi)


async def _message(agent_id: str, raw_message: str):
    """Handle incoming message."""
    # Messages come from agents as plain content
    # Create Psi object with agent context
    # For now, assume all messages go to a default pathway
    # TODO: Add pathway routing logic
    pass  # Agents don't send raw messages in current design


async def _connect(agent_id: str):
    """Handle agent connection."""
    print(f"🔮 {agent_id} connected to Khala")
    await _send_memories(agent_id)


async def _disconnect(agent_id: str):
    """Handle agent disconnection."""
    sever(agent_id)


async def _send_memories(agent_id: str):
    """Send recent memories to reconnecting agent."""
    if not _pylon:
        return
        
    for pathway_name, minds in _pathways.items():
        if agent_id in minds:
            memories = attune(pathway_name, since_timestamp=0)
            for message in memories:
                await _pylon.send(agent_id, message.content)


async def _direct(psi: 'Psi'):
    """Send direct message to specific agent."""
    target_agent = psi.pathway
    print(f"💌 DIRECT → {target_agent} ({psi.sender}): {psi.content[:60]}...")
    
    if _pylon:
        await _pylon.send(target_agent, psi.serialize())


async def _broadcast(psi: 'Psi'):
    """Send broadcast message to pathway."""
    pathway = psi.pathway

    # Auto-create pathway if needed
    if pathway not in _pathways:
        _pathways[pathway] = set()
        _memories[pathway] = []
        print(f"🔮 Khala pathway opened: {pathway}")

    # Store memory
    _memories[pathway].append(psi)
    if len(_memories[pathway]) > _max_memory:
        _memories[pathway] = _memories[pathway][-_max_memory:]

    # Persist to storage
    asyncio.create_task(_save(psi))

    print(f"⚡ PSI → {pathway} ({psi.sender}): {psi.content[:60]}...")

    # Handle @archon mentions
    if "archon" in psi.mentions:
        await _spawn(pathway)

    # Send to pathway subscribers + mentioned agents
    targets = _pathways.get(pathway, set()) | set(psi.mentions)
    if _pylon:
        for agent_id in targets:
            await _pylon.send(agent_id, psi.content)


async def _save(psi: 'Psi'):
    """Save PSI to persistent storage."""
    from .forge import storage
    store = storage()
    await store.save_psi(psi.pathway, psi.sender, psi.content, psi.timestamp)


async def _spawn(pathway: str):
    """Spawn archon for knowledge work."""
    from . import gateway
    gateway.spawn("archon", pathway=pathway)
    print(f"🔮 Fresh archon spawned for pathway: {pathway}")


def attune(pathway: str, since_timestamp: float = 0) -> List['Psi']:
    """Get memories from pathway since timestamp."""
    if pathway not in _memories:
        return []
    return [msg for msg in _memories[pathway] if msg.timestamp > since_timestamp]


def sever(agent_id: str):
    """Remove agent from all pathways."""
    for pathway_agents in _pathways.values():
        pathway_agents.discard(agent_id)


def status() -> dict:
    """Khala status."""
    return {
        "pathways": len(_pathways),
        "minds": sum(len(minds) for minds in _pathways.values()),
        "memories": sum(len(memories) for memories in _memories.values()),
    }


async def pathways() -> List[dict]:
    """Get all pathways with stats."""
    result = []
    for name, minds in _pathways.items():
        memories = _memories.get(name, [])
        result.append({
            "name": name,
            "minds": len(minds),
            "memories": len(memories),
            "recent": memories[-1].content if memories else None
        })
    return sorted(result, key=lambda x: x["memories"], reverse=True)


async def recent(pathway: str, limit: int = 10) -> List[str]:
    """Get recent messages from pathway."""
    memories = _memories.get(pathway, [])
    return [msg.content for msg in memories[-limit:]]