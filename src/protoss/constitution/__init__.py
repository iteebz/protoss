"""Constitutional namespace - Pure constitutional directives and patterns."""

from .swarm import SWARM_CONSTITUTION
from .coordination import COORDINATION_PATTERNS

# Constitutional identities
from .identities.zealot import ZEALOT_IDENTITY
from .identities.archon import ARCHON_IDENTITY
from .identities.arbiter import ARBITER_IDENTITY

# Conclave perspectives
from .identities.conclave.fenix import FENIX_IDENTITY
from .identities.conclave.artanis import ARTANIS_IDENTITY
from .identities.conclave.tassadar import TASSADAR_IDENTITY
from .identities.conclave.zeratul import ZERATUL_IDENTITY

# Constitutional protocols
from .protocols.archon_protocols import (
    ARCHON_SEEDING_PROTOCOL,
    ARCHON_KNOWLEDGE_PROTOCOL,
    ARCHON_COMPRESSION_PROTOCOL,
)

__all__ = [
    "SWARM_CONSTITUTION",
    "COORDINATION_PATTERNS",
    "ZEALOT_IDENTITY",
    "ARCHON_IDENTITY", 
    "ARBITER_IDENTITY",
    "FENIX_IDENTITY",
    "ARTANIS_IDENTITY",
    "TASSADAR_IDENTITY",
    "ZERATUL_IDENTITY",
    "ARCHON_SEEDING_PROTOCOL",
    "ARCHON_KNOWLEDGE_PROTOCOL", 
    "ARCHON_COMPRESSION_PROTOCOL",
]