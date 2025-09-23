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
    """Storage protocol for Bus event persistence."""

    async def save_event(self, event: Dict) -> None:
        """Save structured coordination event.

        Args:
            event: Event dictionary with type, channel, sender, timestamp, etc.
        """
        ...

    async def load_events(
        self,
        event_type: Optional[str] = None,
        coordination_id: Optional[str] = None,
        channel: Optional[str] = None,
        sender: Optional[str] = None,
        since: float = 0,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Load coordination events with filtering.

        Args:
            event_type: Filter by event type (agent_spawn, agent_message, etc.)
            coordination_id: Filter by coordination session
            channel: Filter by channel
            sender: Filter by sender
            since: Timestamp to load events since
            limit: Maximum number of events

        Returns:
            List of event dictionaries
        """
        ...

    async def load_coordinations(self) -> List[Dict]:
        """Load coordination session metadata.

        Returns:
            List of coordination dictionaries with id, created_at, last_active, event_count
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
