"""Constitutional AI agent with configurable perspectives."""

from typing import Dict
import logging as _logging

from .unit import Unit
from ..constitution import (
    ARTANIS_IDENTITY,
    FENIX_IDENTITY,
    TASSADAR_IDENTITY,
    ZERATUL_IDENTITY,
)
from ..core.config import Config
from ..core import parser  # Corrected parser import

logger = _logging.getLogger(__name__)


class Conclave(Unit):
    """Constitutional AI agent with perspective-based identity."""

    def __init__(
        self,
        perspective: str,
        agent_id: str,
        agent_type: str,
        channel_id: str,
        config: Config,
    ):
        super().__init__(agent_id, agent_type, channel_id, config)
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

    async def perform_review(self, review_id: str, channel_id: str) -> str:
        """Performs a constitutional review on an archived artifact summary."""
        logger.info(
            f"{self.agent_id} performing constitutional review on {review_id} in {channel_id}"
        )

        # 1. Accept the Chalice
        await self.broadcast(f"!reviewing {review_id}")

        # 2. Request summary from Archon naturally  
        await self.broadcast(f"@archon can you provide summary for {review_id}?")

        # 3. Listen for Archon's natural response
        response_message = await self.poll_channel_for_response(
            timeout=30,
            content_filter=review_id,  # Look for messages mentioning the review_id
        )

        if not response_message:
            await self.broadcast(f"No response from Archon for {review_id}. !despawn")
            return "Review failed: No Archon response."

        # 4. Perform Review
        summary_content = response_message.get("content", "")
        review_comments = await super().__call__(
            f"Review the following summary for constitutional adherence:\n\n{summary_content}"
        )

        # 5. Broadcast Judgment
        judgment = (
            "approve"
            if "constitutionally sound" in review_comments.lower()
            else "reject"
        )  # Simplified judgment
        await self.broadcast(f"!reviewed {review_id} {judgment} {review_comments}")

        # 6. Despawn
        await self.broadcast("!despawn")
        return f"Constitutional review complete: {judgment} for {review_id}."
