"""Message data structures for agent coordination."""

import time
from dataclasses import dataclass, field


@dataclass
class Message:
    """Message for agent coordination."""

    channel: str  # Target channel or agent_id for direct messages
    sender: str  # Agent ID that created this message
    content: str  # Message content with potential @mentions
    timestamp: float = field(default_factory=time.time)  # Unix timestamp

    def serialize(self) -> str:
        """Serialize for transmission."""
        return self.content
