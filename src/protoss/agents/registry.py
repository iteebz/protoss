"""Constitutional Agent Registry - Single source of truth for all agent metadata."""

from ..constitution.identities import (
    ZEALOT_IDENTITY,
    ARCHON_IDENTITY,
    ARBITER_IDENTITY,
    ORACLE_IDENTITY,
    TASSADAR_IDENTITY,
    ZERATUL_IDENTITY,
    ARTANIS_IDENTITY,
    FENIX_IDENTITY,
)
from ..constitution.guidelines import (
    ZEALOT_GUIDELINES,
    ARCHON_GUIDELINES,
    ARBITER_GUIDELINES,
    ORACLE_GUIDELINES,
    CONCLAVE_GUIDELINES,
)

AGENT_REGISTRY = {
    "zealot": {
        "identity": [ZEALOT_IDENTITY],
        "guidelines": ZEALOT_GUIDELINES,
        "tools": ["file", "system"],
    },
    "archon": {
        "identity": [ARCHON_IDENTITY],
        "guidelines": ARCHON_GUIDELINES,
        "tools": ["file"],
    },
    "arbiter": {
        "identity": [ARBITER_IDENTITY],
        "guidelines": ARBITER_GUIDELINES,
        "tools": [],
    },
    "oracle": {
        "identity": [ORACLE_IDENTITY],
        "guidelines": ORACLE_GUIDELINES,
        "tools": ["web"],
    },
    "conclave": {
        "identity": [
            TASSADAR_IDENTITY,
            ZERATUL_IDENTITY,
            ARTANIS_IDENTITY,
            FENIX_IDENTITY,
        ],
        "guidelines": CONCLAVE_GUIDELINES,
        "tools": [],
    },
}


def get_agent_names() -> list[str]:
    """Returns all agent names from constitutional registry, including special cases like Probe."""
    llm_agent_names = list(AGENT_REGISTRY.keys())
    # Probe is a heuristic agent, not LLM-driven, but needs to be recognized by the parser.
    return llm_agent_names + ["probe"]
