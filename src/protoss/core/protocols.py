"""Core storage protocol for protoss."""

from dataclasses import asdict, dataclass
from typing import Protocol, runtime_checkable, Dict


@dataclass
class Message:
    """A single message in conversation."""

    sender: str
    content: str
    timestamp: float
    channel: str = "human"

    def to_dict(self) -> Dict:
        return asdict(self)


@runtime_checkable
class Storage(Protocol):
    """Storage protocol for the conversation ledger."""

    async def save_message(
        self, channel: str, sender: str, content: str, timestamp: float
    ) -> None:
        """Save single message to the ledger. Raises on failure."""
        ...

    async def load_messages(
        self, channel: str, since: float | None = None
    ) -> list[dict]:
        """Load messages from the ledger with optional filtering."""
        ...
