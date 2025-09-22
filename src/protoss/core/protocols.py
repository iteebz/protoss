"""Protocols for Protoss coordination infrastructure."""

from typing import Protocol, List, Dict, Optional
from dataclasses import dataclass


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
class Signal:
    """Base class for all constitutional signals."""
    pass


@dataclass
class Mention(Signal):
        """Represents an @mention of an agent or perspective."""
        agent_name: str

    @dataclass
    class Spawn(Signal):
        """Represents an @spawn request for an agent type."""
        agent_type: str

    @dataclass
    class Completion(Signal):
        """Represents a !complete signal."""
        pass

    @dataclass
    class Despawn(Signal):
        """Represents a !despawn signal."""
        pass

    @dataclass
    class Archive(Signal):
        """Represents an !archive request."""
        summary: str

    @dataclass
    class Review(Signal):
        """Represents a !review <review_id> request."""
        review_id: str

    @dataclass
    class Reviewing(Signal):
        """Represents a !reviewing <review_id> signal."""
        review_id: str

    @dataclass
    class Reviewed(Signal):
        """Represents a !reviewed <review_id> [judgment] signal."""
        review_id: str
        judgment: str

