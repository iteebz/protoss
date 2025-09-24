"""Message data structures for agent coordination."""

import time
from dataclasses import dataclass, field
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
    msg_type: str = "event"  # Protocol message type
    coordination_id: Optional[str] = None  # Coordination tracking ID

    def to_dict(self) -> Dict:
        """Convert message to dictionary format."""
        return {
            "channel": self.channel,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "signals": [signal.to_dict() for signal in self.signals],
            "event": self.event,
            "msg_type": self.msg_type,
            "coordination_id": self.coordination_id,
        }

    def serialize(self) -> str:
        """Serialize the message to a JSON string."""
        import json

        return json.dumps(self.to_dict())
