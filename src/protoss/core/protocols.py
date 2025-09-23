"""Protocols for Protoss coordination infrastructure."""

from typing import Protocol, List, Dict, Optional, Union, Type
from dataclasses import dataclass, field, asdict


@dataclass
class BaseSignal:
    """Base class for all signals."""

    type: str = field(init=False)

    def to_dict(self) -> Dict:
        """Returns a dictionary representation of the signal, including its type."""
        data = asdict(self)
        data["type"] = self.type  # Explicitly add the type field
        return data

    @classmethod
    def deserialize(cls, signal_dict: Dict) -> Optional["BaseSignal"]:
        """Deserializes a signal dictionary into the appropriate Signal object."""
        signal_type = signal_dict.get("type")
        if not signal_type:
            return None

        signal_class = _signal_registry.get(signal_type)
        if not signal_class:
            return None

        # Remove 'type' from dict before passing to dataclass constructor
        # as it's set by default=... and init=False
        clean_dict = {k: v for k, v in signal_dict.items() if k != "type"}
        return signal_class(**clean_dict)


class Storage(Protocol):
    """Storage protocol for Bus channel persistence."""

    async def save_message(
        self, channel: str, sender: str, content: str, timestamp: float = None
    ) -> None:
        """Save message transmission to channel.

        Args:
            channel: Channel name to save to
            sender: Agent ID sending the message
            content: Message content
            timestamp: Optional timestamp (uses current time if None)
        """
        ...

    async def load_messages(
        self, channel: str, since: float = 0, limit: Optional[int] = None
    ) -> List[Dict]:
        """Load message transmissions from channel since timestamp.

        Args:
            channel: Channel name to load from
            since: Timestamp to load messages since (0 for all)
            limit: Maximum number of messages to return

        Returns:
            List of message dictionaries with sender, content, timestamp
        """
        ...

    async def load_channels(self) -> List[Dict]:
        """Load all channels with activity stats.

        Returns:
            List of channel dictionaries with name, created_at, last_active, message_count
        """
        ...

    async def recent(self, channel: str, limit: int = 10) -> List[str]:
        """Get recent message content from channel.

        Args:
            channel: Channel name
            limit: Number of recent messages to return

        Returns:
            List of recent message content strings
        """
        ...


@dataclass
class Mention(BaseSignal):
    """@mention signal."""

    type: str = field(default="Mention", init=False)
    agent_name: str


@dataclass
class Despawn(BaseSignal):
    """!despawn signal."""

    type: str = field(default="Despawn", init=False)


@dataclass
class Emergency(BaseSignal):
    """!emergency signal."""

    type: str = field(default="Emergency", init=False)


Signal = Union[Mention, Despawn, Emergency]

_signal_registry: Dict[str, Type[BaseSignal]] = {
    "Mention": Mention,
    "Despawn": Despawn,
    "Emergency": Emergency,
}
