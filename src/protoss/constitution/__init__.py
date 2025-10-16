"""Constitutional identities for Protoss agents."""

from .coordination import DEFAULT_AGENTS, EXIT_SIGNALS, COMPLETION_SIGNAL, GUIDELINES
from .harbinger import IDENTITY as HARBINGER_IDENTITY
from .sentinel import IDENTITY as SENTINEL_IDENTITY
from .zealot import IDENTITY as ZEALOT_IDENTITY

CONSTITUTIONS = {
    "harbinger": HARBINGER_IDENTITY,
    "sentinel": SENTINEL_IDENTITY,
    "zealot": ZEALOT_IDENTITY,
}

__all__ = ["DEFAULT_AGENTS", "EXIT_SIGNALS", "COMPLETION_SIGNAL", "CONSTITUTIONS", "GUIDELINES"]
