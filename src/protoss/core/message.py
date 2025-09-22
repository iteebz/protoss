"""Message data structures for agent coordination."""

import time
from typing import List, Optional, Dict
from ..core.protocols import Signal


@dataclass
class Message:
    """Message for agent coordination."""

    channel: str  # Target channel or agent_id for direct messages
    sender: str  # Agent ID that created this message
    timestamp: float = field(default_factory=time.time)  # Unix timestamp
    signals: List[Signal] = field(default_factory=list)  # Parsed @ and ! commands
    event: Optional[Dict] = (
        None  # Structured cogency events (think, respond, call, result)
    )
