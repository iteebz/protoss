"""Pure spawning functions for agent processes."""

import asyncio
import logging
import sys
import json
from typing import Dict, Set, List

from ..constitution import AGENT_IDENTITIES

logger = logging.getLogger(__name__)

# Agent registry - maps agent types to their module paths
AGENTS = {
    "zealot": "protoss.agents.zealot",
    "archon": "protoss.agents.archon",
    "arbiter": "protoss.agents.arbiter",
    "oracle": "protoss.agents.oracle",
    "conclave": "protoss.agents.conclave",
}


async def spawn_agent(agent_type: str, channel: str, bus_url: str) -> List[int]:
    """Spawn agent process(es). Returns list of PIDs."""
    if agent_type not in AGENT_IDENTITIES:
        raise ValueError(f"Unknown agent type: {agent_type}")

    pids = []

    # Special case: conclave spawns 4 Sacred Four processes
    if agent_type == "conclave":
        sacred_four = ["tassadar", "zeratul", "artanis", "fenix"]
        for sacred_name in sacred_four:
            agent_id = f"{sacred_name}-{asyncio.get_event_loop().time():.0f}"
            identity_param = {"identity": sacred_name}

            cmd = [
                sys.executable,
                "-m",
                "protoss.agents.conclave",
                "--agent-id",
                agent_id,
                "--agent-type",
                "conclave",
                "--channel",
                channel,
                "--bus-url",
                bus_url,
                "--params",
                json.dumps(identity_param),
            ]

            process = await asyncio.create_subprocess_exec(*cmd)
            logger.info(f"Spawned Sacred Four {agent_id} PID {process.pid}")
            pids.append(process.pid)

    else:
        # Normal single agent spawn
        if agent_type not in AGENTS:
            raise ValueError(f"No module mapping for agent type: {agent_type}")

        module = AGENTS[agent_type]
        agent_id = f"{agent_type}-{asyncio.get_event_loop().time():.0f}"

        cmd = [
            sys.executable,
            "-m",
            module,
            "--agent-id",
            agent_id,
            "--agent-type",
            agent_type,
            "--channel",
            channel,
            "--bus-url",
            bus_url,
        ]

        process = await asyncio.create_subprocess_exec(*cmd)
        logger.info(f"Spawned {agent_id} PID {process.pid}")
        pids.append(process.pid)

    return pids


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
