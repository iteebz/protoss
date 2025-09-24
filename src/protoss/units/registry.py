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

UNIT_REGISTRY = {
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
    "probe": {
        "identity": [],
        "guidelines": [],
        "tools": [],
    },
}


def get_unit_names() -> list[str]:
    """Returns all unit names from constitutional registry."""
    return list(UNIT_REGISTRY.keys())


def get_unit_data(unit_type: str) -> dict:
    """Get unit configuration from registry."""
    return UNIT_REGISTRY.get(unit_type)
