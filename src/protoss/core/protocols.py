"""Core storage protocol for protoss."""

from dataclasses import asdict, dataclass
from typing import Protocol, runtime_checkable


@dataclass
class Message:
    """A single message in conversation."""

    sender: str
    content: str
    timestamp: float
    channel: str = "human"

    def to_dict(self) -> dict:
        return asdict(self)


@runtime_checkable
class Storage(Protocol):
    """Storage protocol for the conversation ledger."""

    async def save_message(
        self,
        channel: str,
        sender: str,
        content: str,
        timestamp: float | None = None,
        parent: str | None = None,
    ) -> None:
        """Save single message to the ledger. Raises on failure."""
        ...

    async def load_messages(self, channel: str, since: float | None = None) -> list[dict]:
        """Load messages from the ledger with optional filtering."""
        ...

    async def get_channels(self) -> list[str]:
        """Get list of active channels."""
        ...

    async def get_parent_channel(self, channel: str) -> str | None:
        """Get parent channel for a given channel."""
        ...

    async def start_run(self, run_id: str, task: str, agents: list[str], channel: str) -> None:
        """Record start of a coordination run."""
        ...

    async def complete_run(self, run_id: str, outcome: str, msg_count: int) -> None:
        """Record completion of a coordination run."""
        ...
