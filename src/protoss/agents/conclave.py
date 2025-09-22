"""Constitutional AI agent with configurable perspectives."""

from typing import Dict
from .unit import Unit
from ..constitution import (
    FENIX_IDENTITY,
    ARTANIS_IDENTITY,
    TASSADAR_IDENTITY,
    ZERATUL_IDENTITY,
)


class Conclave(Unit):
    """Constitutional AI agent with perspective-based identity."""

    def __init__(self, perspective: str, agent_id: str = None, max_cycles: int = 100):
        super().__init__(agent_id, max_cycles=max_cycles)
        self.perspective = perspective

        if perspective not in self.PERSPECTIVES:
            raise ValueError(f"Unknown perspective: {perspective}")

    @property
    def tools(self):
        """Pure constitutional reasoning - no external tools needed."""
        return []

    @property
    def identity(self) -> str:
        """Get constitutional identity for this perspective."""
        return self.PERSPECTIVES[self.perspective]["identity"]

    @property
    def emoji(self) -> str:
        """Get emoji for this perspective."""
        return self.PERSPECTIVES[self.perspective]["emoji"]

    @property
    def action(self) -> str:
        """Get action verb for this perspective."""
        return self.PERSPECTIVES[self.perspective]["action"]

    async def respond_to_mention(self, mention_context: str, channel_id: str) -> str:
        """Provide immediate constitutional perspective when summoned."""

        summary = (mention_context or "").strip()
        if not summary:
            summary = "No explicit context specified."
        header = f"{self.emoji} {self.perspective.upper()} perspective {self.action}"
        return (
            f"{header}\n"
            f"Channel: {channel_id}\n"
            f"Context received: {summary}\n"
            "Preparing full constitutional deliberation."
        )

    # Conclave uses base.py cogency coordination with no tools - pure constitutional reasoning

    # Constitutional perspectives using extracted constitutional identities
    PERSPECTIVES: Dict[str, Dict[str, str]] = {
        "fenix": {
            "emoji": "⚡",
            "action": "charging",
            "identity": FENIX_IDENTITY,
        },
        "artanis": {
            "emoji": "🏛️",
            "action": "synthesizing",
            "identity": ARTANIS_IDENTITY,
        },
        "tassadar": {
            "emoji": "🔮",
            "action": "deliberating",
            "identity": TASSADAR_IDENTITY,
        },
        "zeratul": {
            "emoji": "👤",
            "action": "investigating",
            "identity": ZERATUL_IDENTITY,
        },
    }
