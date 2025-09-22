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

    async def coordinate(self):
        """The Conclave's primary execution loop, implementing the Core Coordination Pattern."""
        logger.info(
            f"{self.id} ({self.perspective}) entering coordination loop in {self.channel_id}."
        )
        self.despawned = False
        full_context = ""

        # --- The Outer Loop: The Agent's Life --- #
        while not self.despawned:
            # 1. Listen: Get all new messages since our last turn.
            full_context = await self._get_full_channel_history()

            if "Error:" in full_context:
                logger.error(f"{self.id} failed to get context, despawning.")
                break

            logger.info(f"{self.id} starting cognitive turn...")

            # 2. Reason & Act: The Inner Cognitive Turn (The Cogency Engine)
            # The Conclave's constitutional identity for its specific perspective
            # will guide it to deliberate on the context and provide its judgment.
            async for event in self(full_context):
                if event["type"] == "respond":
                    content = event.get("content", "")
                    await self.broadcast(event)
                    if "!despawn" in content:
                        self.despawned = True

                elif event["type"] == "think":
                    logger.debug(f"{self.id} is thinking: {event.get('content', '')}")

                elif event["type"] == "end":
                    logger.info(
                        f"{self.id} ended cognitive turn, will listen for updates."
                    )
                    break

        logger.info(f"{self.id} has despawned and is terminating.")

    async def _get_full_channel_history(self) -> str:
        """Requests and retrieves the full channel history from the Bus."""
        try:
            await self.bus_client.send_json(
                {"type": "history_req", "channel": self.channel_id}
            )

            history_response = await self.bus_client.receive_json()

            if history_response.get("type") != "history_resp":
                logger.error(f"{self.id} did not receive a valid history response.")
                return "Error: Invalid history response."

            channel_events = history_response.get("history", [])
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
