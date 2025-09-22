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

    async def coordinate(self):
        """The Zealot's primary execution loop, implementing the Core Coordination Pattern.

        This method embodies the two-level loop described in `emergence.md`:
        1. The Outer Loop (`while not self.despawned`): Listens for team updates.
        2. The Inner Loop (`async for event in self(...)`): Executes the agent's cognitive turn.
        """
        logger.info(
            f"{self.id} entering coordination loop in channel {self.channel_id}."
        )
        self.despawned = False
        full_context = ""

        # --- The Outer Loop: The Agent's Life --- #
        while not self.despawned:
            # 1. Listen: Get all new messages since our last turn.
            # In a real implementation, this would be a more sophisticated diff.
            # For now, we get the full history and use it as the complete context.
            full_context = await self._get_full_channel_history()

            if "Error:" in full_context:
                logger.error(f"{self.id} failed to get context, despawning.")
                break

            logger.info(f"{self.id} starting cognitive turn...")

            # 2. Reason & Act: The Inner Cognitive Turn (The Cogency Engine)
            async for event in self(full_context):
                if event["type"] == "respond":
                    content = event.get("content", "")
                    await self.broadcast(event)
                    # The agent sovereignly chooses to despawn within a response.
                    if "!despawn" in content:
                        self.despawned = True

                elif event["type"] == "think":
                    logger.debug(f"{self.id} is thinking: {event.get('content', '')}")

                elif event["type"] == "end":
                    # The agent has ended its cognitive turn and is ready for new input.
                    logger.info(
                        f"{self.id} ended cognitive turn, will listen for updates."
                    )
                    break  # Break inner loop to re-enter outer `listen` loop.

        logger.info(f"{self.id} has despawned and is terminating.")

    async def _get_full_channel_history(self) -> str:
        """Requests and retrieves the full channel history from the Bus."""
        try:
            await self.bus_client.send_json(
                {"type": "history_req", "channel": self.channel_id}
            )

            # This is a simplified receive; a real implementation would be more robust.
            history_response = await self.bus_client.receive_json()

            if history_response.get("type") != "history_resp":
                logger.error(f"{self.id} did not receive a valid history response.")
                return "Error: Invalid history response."

            channel_events = history_response.get("history", [])
            # Reconstruct the conversational context from the event history.
            if not channel_events:
                return "The channel is empty. You are the first to act."
            return "\n".join(
                [
                    f"{event.get('sender')}: {event.get('content', '')}"
                    for event in channel_events
                ]
            )
        except Exception as e:
            logger.error(f"{self.id} exception while getting channel history: {e}")
            return f"Error: Exception getting history - {e}"
