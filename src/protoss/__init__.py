"""Constitutional AI swarm coordination."""

from .core.protoss import Protoss

# Constitutional constants are internally consumed and not part of the public API
# They should be imported by the modules that need them (e.g., agents)

__all__ = ["Protoss"]
