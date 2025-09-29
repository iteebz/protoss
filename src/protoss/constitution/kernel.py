from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protoss.core.event import Event

AGENT_TYPES = {
    "arbiter",
    "zealot",
    "archon",
    "oracle",
    "fenix",
    "tassadar",
    "zeratul",
    "artanis",
}


def validate_spawn(agent_type: str) -> bool:
    return agent_type in AGENT_TYPES


def validate_sovereignty(agent_id: str, deregistering_id: str) -> bool:
    return agent_id == deregistering_id


def validate_coordination(event: "Event") -> bool:
    critical_types = {"agent_message", "tool_output"}
    return event.type not in critical_types or event.coordination_id is not None
