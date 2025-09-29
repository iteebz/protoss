"""Pure spawning functions for agent processes."""

import asyncio
import logging
import sys
import json
from typing import Dict, Set, List

from ..constitution.registry import AGENT_REGISTRY

logger = logging.getLogger(__name__)


async def spawn_agent(
    agent_type: str, channel: str, bus_url: str, coordination_id: str = None
) -> List[int]:
    """Spawn agent process(es). Returns list of PIDs."""
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent type: {agent_type}")

    pids = []
    registry_data = AGENT_REGISTRY[agent_type]
    identities = registry_data["identity"]
    module = "protoss.core.agent"

    # Multi-identity case (conclave): spawn multiple processes
    if len(identities) > 1:
        sacred_names = [
            "tassadar",
            "zeratul",
            "artanis",
            "fenix",
        ]  # Constitutional Sacred Four
        for i, sacred_name in enumerate(sacred_names):
            agent_id = f"{sacred_name}-{asyncio.get_event_loop().time():.0f}"
            identity_param = {"identity_index": i}

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
                "--params",
                json.dumps(identity_param),
            ]

            if coordination_id:
                cmd.extend(["--coordination-id", coordination_id])

            process = await asyncio.create_subprocess_exec(*cmd)
            logger.info(f"Spawned Sacred Four {agent_id} PID {process.pid}")
            pids.append(process.pid)

    else:
        # Single identity case: spawn one process
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

        if coordination_id:
            cmd.extend(["--coordination-id", coordination_id])

        process = await asyncio.create_subprocess_exec(*cmd)
        logger.info(f"Spawned {agent_id} PID {process.pid}")
        pids.append(process.pid)

    return pids


def should_spawn_agent(
    agent_type: str,
    channel: str,
    active_agents: Dict[str, Set[str]],
    max_agents: int = 10,
) -> bool:
    """Determine if agent should be spawned."""
    if agent_type not in AGENT_REGISTRY:
        return False

    channel_agents = active_agents.get(channel, set())

    # Check max agents per channel
    if len(channel_agents) >= max_agents:
        return False

    # Check if agent type already active in channel
    if any(aid.startswith(f"{agent_type}-") for aid in channel_agents):
        return False

    return True
