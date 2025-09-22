"""Arbiter - Human command interface for Protoss swarm coordination."""

from .unit import Unit
import logging
from ..core.config import Config
from ..constitution import ARBITER_IDENTITY
from ..core import parser  # Corrected parser import

logger = logging.getLogger(__name__)


class Arbiter(Unit):
    """⚔️ Human command interface connected to Protoss swarm."""

    def __init__(self, agent_id: str, agent_type: str, channel_id: str, config: Config):
        super().__init__(agent_id, agent_type, channel_id, config)

    @property
    def identity(self) -> str:
        return ARBITER_IDENTITY

    @property
    def tools(self):
        """Arbiter convenes with other agents, no direct file access needed."""
        return []

    async def respond_to_mention(self, mention_context: str, channel_id: str) -> str:
        """Respond to a human's mention by generating a diplomatic response."""
        logger.info(f"{self.agent_id} responding to human mention in {channel_id}")

        # Use the Arbiter's LLM capabilities to formulate a response
        response = await super().__call__(mention_context)

        return response

    async def perform_review(self, review_id: str, channel_id: str) -> str:
        """Facilitates human review of an archived artifact summary."""
        logger.info(
            f"{self.agent_id} facilitating human review on {review_id} in {channel_id}"
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

        # 4. Present to Human (simulated)
        summary_content = response_message.get("content", "")
        human_presentation = await super().__call__(
            f"Prepare a concise summary for human review of the following:\n\n{summary_content}\n\nBased on this, should the work be approved or rejected? Provide a brief justification."
        )

        # 5. Simulate Human Judgment (for now, LLM decides)
        # In a real scenario, this would involve interaction with the 'protoss ask' interface.
        judgment_decision = await super().__call__(
            f"Based on the following human presentation, decide if the work should be 'approve' or 'reject'. Only respond with 'approve' or 'reject'.\n\n{human_presentation}"
        )
        judgment = judgment_decision.strip().lower()
        if judgment not in ["approve", "reject"]:
            judgment = "reject"  # Default to reject if LLM is unclear

        # 6. Broadcast Judgment
        await self.broadcast(f"!reviewed {review_id} {judgment} {human_presentation}")

        # 7. Despawn
        await self.broadcast("!despawn")
        return f"Human review complete: {judgment} for {review_id}."
