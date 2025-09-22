"""Pure spawning functions for agent processes."""

import asyncio
import logging
import sys
from typing import Dict, Set

logger = logging.getLogger(__name__)

# Agent registry
AGENTS = {
    "zealot": "protoss.agents.zealot",
    "archon": "protoss.agents.archon",
    "conclave": "protoss.agents.conclave",
    "arbiter": "protoss.agents.arbiter",
    "oracle": "protoss.agents.oracle",
}


async def spawn_agent(agent_type: str, channel: str, bus_url: str) -> int:
    """Spawn agent process. Returns PID."""
    if agent_type not in AGENTS:
        raise ValueError(f"Unknown agent type: {agent_type}")

    module = AGENTS[agent_type]
    agent_id = f"{agent_type}-{asyncio.get_event_loop().time():.0f}"

    cmd = [
        sys.executable,
        "-m",
        module,
        "--agent-id",
        agent_id,
        "--channel",
        channel,
        "--bus-url",
        bus_url,
    ]

    process = await asyncio.create_subprocess_exec(*cmd)
    logger.info(f"Spawned {agent_id} PID {process.pid}")
    return process.pid


def should_spawn(
    agent_type: str,
    channel: str,
    active_agents: Dict[str, Set[str]],
    max_agents: int = 10,
) -> bool:
    """Determine if agent should be spawned."""
    if agent_type not in AGENTS:
        return False

    channel_agents = active_agents.get(channel, set())

    # Check max agents per channel
    if len(channel_agents) >= max_agents:
        return False

    # Check if agent type already active in channel
    if any(aid.startswith(f"{agent_type}-") for aid in channel_agents):
        return False

    return True
