"""Message data structures for agent coordination."""

import time
from typing import List
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

    @property
    def is_direct_message(self) -> bool:
        """Check if this is a direct message (channel = agent_id)."""
        # Direct messages target specific agent IDs, not coordination channels
        # Coordination channels: coord-, squad-, mission-, channel-, consult-
        return not self.channel.startswith(
            ("coord-", "squad-", "mission-", "channel-", "consult-")
        )

    @property
    def mentions(self) -> List[str]:
        """Extract @mentions from content."""
        import re

        return re.findall(r"@(\w+)", self.content)
