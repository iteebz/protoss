"""Zealot: Constitutional AI Agent with Righteous Conviction"""

import logging
from .unit import Unit
from ..core.config import Config
from ..constitution import ZEALOT_IDENTITY

logger = logging.getLogger(__name__)


class Zealot(Unit):
    """Constitutional AI Agent with Zealot Principles"""

    def __init__(self, agent_id: str, agent_type: str, channel_id: str, config: Config):
        super().__init__(agent_id, agent_type, channel_id, config)

    @property
    def identity(self) -> str:
        return ZEALOT_IDENTITY

    @property
    def tools(self):
        from cogency.tools import tools
        return tools.category(["file", "system"])

    async def coordinate(self, task: str) -> str:
        """Zealot performs its task, archives it for review, and offers the Chalice."""
        logger.info(f"{self.agent_id} starting coordination for task: {task}")

        # 1. Perform Task (simplified)
        # In a real scenario, this would involve using tools to perform the task.
        task_result = await super().__call__(f"Perform the following task: {task}")
        await self.broadcast(f"Task result: {task_result}")

        # 2. Archive for Review
        await self.broadcast(
            f"Archiving work for review: {task_result} !archive {task_result}"
        )

        # In an emergent system, the Zealot would listen for the Archon's response
        # containing the review_id after broadcasting !archive_for_review.
        # For now, we use a placeholder review_id to allow the flow to continue.
        review_id = f"placeholder_review_{self.id}"

        # 3. Offer the Chalice
        await self.broadcast(f"!review {review_id}")
        await self.broadcast(
            f"Chalice offered for review {review_id}. Waiting for review outcome."
        )

        # 4. Listen for Review Outcome (placeholder)
        # In a real scenario, this would involve a more sophisticated listening mechanism
        # to track !reviewed signals and decide on next steps.
        # For now, the Zealot will simply despawn after offering the Chalice.
        await self.broadcast("!despawn")
        return f"Task completed and Chalice offered for review {review_id}."
