"""Protoss units: Individual agents in the coordination swarm."""

from typing import Protocol
from cogency import Agent

class Unit(Protocol):
    """Canonical unit interface for polymorphic coordination."""
    
    id: str
    identity: str       # Constitutional framework (who am I?)
    tools: list         # Weapons/capabilities (what can I do?)
    agent: Agent        # Cognitive substrate (how do I think?)
    
    async def execute(self, task: str, pathway: str) -> None:
        """Stream consciousness while executing task."""
        from ..khala import khala
        
        stream = self.agent(task)
        async for event in stream:
            if event.get("type") == "respond":
                await khala.transmit(pathway, self.id, event.get("content", ""))
    
    async def attune(self, pathway: str, since_timestamp: float = 0) -> list:
        """Absorb consciousness streams from pathway since timestamp."""
        from ..khala import khala
        return khala.attune(pathway, since_timestamp)

from .archon import Archon
from .zealot import Zealot
from .tassadar import Tassadar
from .zeratul import Zeratul
from .artanis import Artanis
from .fenix import Fenix

__all__ = ["Unit", "Archon", "Zealot", "Tassadar", "Zeratul", "Artanis", "Fenix"]
