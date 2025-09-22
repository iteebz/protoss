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
        """Arbiter needs tools to gather context for human translation."""
        return self._cogency_tools(["file_read", "file_list"])

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

        # 2. Request summary from Archon (by broadcasting a signal)
        await self.broadcast(f"get_summary {review_id} @archon")

        # 3. Listen for Archon's response (GetArtifactSignal or GetSummarySignal)
        response_message = await self.poll_channel_for_response(
            sender_filter="archon",
            signal_type_filter=parser.GetArtifactSignal,  # Archon responds with GetArtifactSignal for summary too
            timeout=30,  # Give Archon some time to respond
        )

        summary_content = None
        if response_message:
            signals = parser.parse_signals(response_message.get("content", ""))
            for signal in signals:
                if (
                    isinstance(signal, parser.GetArtifactSignal)
                    and signal.review_id == review_id
                ):
                    # Assuming Archon's response to GetArtifactSignal contains the summary in its content
                    summary_content = response_message.get("content")
                    break

        if not summary_content:
            await self.broadcast(
                f"Failed to retrieve summary for {review_id} from Archon. !despawn"
            )
            await self.broadcast("!despawn")
            return "Review failed: Summary not retrieved."

        # 4. Present to Human (simulated)
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
