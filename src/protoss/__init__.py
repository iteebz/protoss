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

from .core.protoss import Protoss as _Protoss
from .core.config import Config
from .agents import Zealot, Arbiter, Conclave
from .core.bus import Bus, Message

def protoss(
    vision: str,
    agents: int = 5,
    timeout: int = 3600,
    debug: bool = False,
    rich_context: bool = True,
    max_agents: int = 50,
    **overrides,
):
    """
    The Cathedral Interface.

    Initializes and returns the Protoss coordination engine.

    Usage:
        async with protoss("build auth system") as swarm:
            result = await swarm
    """
    config = Config(
        agents=agents,
        max_agents=max_agents,
        timeout=timeout,
        debug=debug,
        rich_context=rich_context,
        **overrides,
    )
    return _Protoss(vision, config=config)


__version__ = "0.1.0"
__all__ = [
    "protoss",
    "Zealot",
    "Arbiter",
    "Conclave",
    "Bus",
    "Message",
]
