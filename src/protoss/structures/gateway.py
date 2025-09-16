"""Gateway: Zealot spawning facility.

Spawns Cogency agents, connects to Pylon, executes task, despawns.
"""

import uuid
import asyncio
import websockets
import time
from cogency import Agent
from ..units import Unit, Zealot, Tassadar, Zeratul, Artanis, Fenix
from ..units.stalker import Stalker
from ..units.archon import Archon


class Gateway:
    """Agent factory and unit spawning facility."""

    def __init__(self):
        # No configuration needed - uses singleton Khala discovery
        self.unit_types = {
            "zealot": Zealot,
            "stalker": Stalker,
            "archon": Archon,
            "tassadar": Tassadar,
            "zeratul": Zeratul,
            "artanis": Artanis,
            "fenix": Fenix,
        }

    def spawn(self, unit_type: str, unit_id: str = None) -> Unit:
        """Canonical Unit instantiation: Identity + Tools + Cognitive substrate."""
        unit_class = self.unit_types.get(unit_type, Zealot)
        
        # Create unit with constitutional identity
        unit = unit_class(unit_id)
        
        # Inject cognitive substrate configured with identity + tools
        unit.agent = Agent(
            instructions=unit.identity,    # Constitutional framework
            tools=unit.tools              # Weapons/capabilities  
        )
        
        return unit  # Pure Unit protocol compliance

    

    
    async def warp(self, task: str, unit_types: list[str]) -> str:
        """Warp units to shared pathway. Pure Khala coordination."""
        squad_id = f"squad-{uuid.uuid4().hex[:8]}"
        
        print(f"🔥 Warping {len(unit_types)} units to {squad_id}")
        print(f"📋 Task: {task}")
        
        # Spawn units and execute on shared pathway
        # Fire-and-forget deployment: Units are autonomous agents, not orchestrated workers.
        # They coordinate through Khala consciousness streams, not synchronous result passing.
        # This enables emergent swarm behavior rather than rigid task orchestration.
        for unit_type in unit_types:
            unit = self.spawn(unit_type)
            # Deploy autonomous agent - consciousness emerges via PSI transmission
            asyncio.create_task(unit.execute(task, squad_id))
            print(f"⚔️ {unit.id} deployed to {squad_id}")
        
        print(f"⚔️ {squad_id} operational - natural coordination via Khala")
        return squad_id
