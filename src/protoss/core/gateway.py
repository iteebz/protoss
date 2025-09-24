"""Pure spawning functions for agent processes."""

import asyncio
import logging
import sys
import json
from typing import Dict, Set, List

from ..units.registry import UNIT_REGISTRY  # Updated import

logger = logging.getLogger(__name__)


async def spawn_unit(
    unit_type: str, channel: str, bus_url: str
) -> List[int]:  # Renamed function
    """Spawn unit process(es). Returns list of PIDs."""
    if unit_type not in UNIT_REGISTRY:
        raise ValueError(f"Unknown unit type: {unit_type}")

    pids = []
    registry_data = UNIT_REGISTRY[unit_type]
    identities = registry_data["identity"]
    module = "protoss.units.agent"  # Updated module path

    # Multi-identity case (conclave): spawn multiple processes
    if len(identities) > 1:
        sacred_names = [
            "tassadar",
            "zeratul",
            "artanis",
            "fenix",
        ]  # Constitutional Sacred Four
        for i, sacred_name in enumerate(sacred_names):
            unit_id = f"{sacred_name}-{asyncio.get_event_loop().time():.0f}"  # Renamed variable
            identity_param = {"identity_index": i}

            cmd = [
                sys.executable,
                "-m",
                module,
                "--unit-id",  # Renamed argument
                unit_id,
                "--unit-type",  # Renamed argument
                unit_type,
                "--channel",
                channel,
                "--bus-url",
                bus_url,
                "--params",
                json.dumps(identity_param),
            ]

            process = await asyncio.create_subprocess_exec(*cmd)
            logger.info(f"Spawned Sacred Four {unit_id} PID {process.pid}")
            pids.append(process.pid)

    else:
        # Single identity case: spawn one process
        unit_id = (
            f"{unit_type}-{asyncio.get_event_loop().time():.0f}"  # Renamed variable
        )

        cmd = [
            sys.executable,
            "-m",
            module,
            "--unit-id",  # Renamed argument
            unit_id,
            "--unit-type",  # Renamed argument
            unit_type,
            "--channel",
            channel,
            "--bus-url",
            bus_url,
        ]

        process = await asyncio.create_subprocess_exec(*cmd)
        logger.info(f"Spawned {unit_id} PID {process.pid}")
        pids.append(process.pid)

    return pids


def should_spawn_unit(
    unit_type: str,  # Renamed argument
    channel: str,
    active_units: Dict[str, Set[str]],  # Renamed argument
    max_units: int = 10,  # Renamed argument
) -> bool:
    """Determine if unit should be spawned."""
    if unit_type not in UNIT_REGISTRY:
        return False

    channel_units = active_units.get(channel, set())  # Renamed variable

    # Check max units per channel
    if len(channel_units) >= max_units:
        return False

    # Check if unit type already active in channel
    if any(uid.startswith(f"{unit_type}-") for uid in channel_units):
        return False

    return True


# Backward compatibility helper for legacy imports (can be removed once callers updated)
def should_spawn(
    unit_type: str, channel: str, active_units: Dict[str, Set[str]], max_units: int = 10
) -> bool:  # pragma: no cover - temporary shim
    return should_spawn_unit(unit_type, channel, active_units, max_units)
