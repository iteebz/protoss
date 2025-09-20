"""Protoss: Constitutional AI coordination.

Pure concurrency abstraction for emergent agent coordination.

En taro Adun.
"""

# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .core import Protoss, CoordinationEvent
from .config import Config

# Legacy exports for existing code
from .structures import Nexus, Pylon, gateway
from .units import Zealot
from . import conclave
from . import khala
from .khala import Psi

__version__ = "0.1.0"
__all__ = [
    # Primary API
    "Protoss", "Config", "CoordinationEvent",
    # Legacy exports
    "Nexus", "gateway", "Pylon", "Zealot", "conclave", "khala", "Psi"
]
