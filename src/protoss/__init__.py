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

from .core import Protoss, Config
from .agents import Zealot, Arbiter, Conclave
from .core.bus import Bus, Message

__version__ = "0.1.0"
__all__ = [
    "Protoss",
    "Config",
    "Zealot",
    "Arbiter",
    "Conclave",
    "Bus",
    "Message",
]
