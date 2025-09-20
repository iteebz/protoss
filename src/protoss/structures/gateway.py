"""Gateway: Pure spawning functions.

Clean functions for unit spawning and warping.
"""

import uuid
import asyncio
import logging
from cogency import Agent
from ..units.base import Unit
from ..units import Zealot, Tassadar, Zeratul, Artanis, Fenix
from ..units.archon import Archon

logger = logging.getLogger(__name__)

# Unit registry
UNIT_TYPES = {
    "zealot": Zealot,
    "archon": Archon,
    "tassadar": Tassadar,
    "zeratul": Zeratul,
    "artanis": Artanis,
    "fenix": Fenix,
}


def spawn(unit_type: str, unit_id: str = None, pathway: str = None) -> Unit:
    """Spawn unit with identity and tools."""
    unit_class = UNIT_TYPES.get(unit_type, Zealot)
    
    # Create unit with constitutional identity
    unit = unit_class(unit_id)
    
    # Inject cognitive substrate
    unit.agent = Agent(
        instructions=unit.identity,
        tools=unit.tools,
    )
    
    # Note: Reactive @archon mentions handled by pathway monitoring, not gateway spawning
    
    return unit


async def warp(task: str, agent_count: int = 3, unit_types: list = None, pathway_id: str = None) -> str:
    """Natural coordination via shared pathway using Unit.coordinate()."""
    squad_id = pathway_id or f"squad-{uuid.uuid4().hex[:8]}"
    unit_types = unit_types or ["zealot"] * agent_count
    
    logger.info(f"Warping {agent_count} agents to {squad_id}")
    logger.debug(f"Task: {task}")
    
    # Spawn agents and start coordination
    coordination_tasks = []
    for i in range(agent_count):
        unit_type = unit_types[i] if i < len(unit_types) else "zealot"
        unit = spawn(unit_type)
        
        # Each agent coordinates on the same task/pathway
        coordination_future = asyncio.create_task(unit.coordinate(task, squad_id))
        coordination_tasks.append(coordination_future)
        logger.debug(f"{unit.id} ({unit_type}) coordinating on {squad_id}")
    
    logger.info(f"{squad_id} operational - agents coordinating until completion")
    
    # Wait for coordination to complete 
    results = await asyncio.gather(*coordination_tasks, return_exceptions=True)
    successful_results = [r for r in results if not isinstance(r, Exception)]
    failed_count = len(results) - len(successful_results)
    
    if failed_count > 0:
        logger.warning(f"{failed_count}/{len(results)} agents failed during coordination")
    
    logger.info(f"{squad_id} coordination complete")
    
    return f"Squad {squad_id} completed with {len(successful_results)}/{len(results)} successful agents"


async def solo(task: str, agent_type: str = "zealot", pathway_id: str = None) -> str:
    """Single agent coordination."""
    pathway_id = pathway_id or f"solo-{uuid.uuid4().hex[:8]}"
    
    unit = spawn(agent_type)
    logger.info(f"{unit.id} coordinating solo on {pathway_id}")
    
    result = await unit.coordinate(task, pathway_id)
    
    logger.info(f"Solo coordination complete: {result}")
    return result


async def warp_with_context(task: str, agent_count: int = 3, unit_types: list = None, pathway_id: str = None, keywords: list = None) -> str:
    """Archon-seeded coordination with rich context.
    
    Args:
        task: The coordination task
        agent_count: Number of agents to spawn
        unit_types: Types of units to spawn
        pathway_id: Optional pathway ID
        keywords: Optional keywords for archive search
        
    Returns:
        Coordination completion status
    """
    pathway_id = pathway_id or f"squad-{uuid.uuid4().hex[:8]}"
    
    logger.info(f"Starting archon-seeded coordination on {pathway_id}")
    
    # Spawn archon and seed pathway with context
    archon = spawn("archon")
    await archon.seed_pathway(task, pathway_id, keywords)
    
    logger.info(f"Pathway {pathway_id} seeded with context")
    
    # Now spawn zealots into rich context (not empty pathway)
    result = await warp(task, agent_count, unit_types, pathway_id)
    
    # Compress pathway results
    await archon.compress_pathway(pathway_id, final_summary=True)
    
    logger.info(f"Pathway {pathway_id} compressed to archives")
    
    return result