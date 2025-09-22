"""Archon: Constitutional AI Knowledge Specialist

The Archon unit provides institutional memory and context stewardship for
Protoss coordination systems. Functionally, it's a knowledge management agent
that seeds channels with relevant context and compresses coordination outcomes
into persistent archives.

Technical Architecture:
- Archive Management: Creates and maintains structured knowledge repositories
- Context Seeding: Provides rich starting context for coordination channels
- Mention Response: Handles @archon requests with relevant historical context
- Knowledge Compression: Extracts and archives key insights from coordination
- File Operation Tools: Read/write/edit access for archive maintenance

The name 'Archon' evokes the ancient wisdom keeper who bridges past knowledge
with current coordination needs. These agents ensure that constitutional AI
coordination builds on institutional memory rather than starting fresh each time.

Design Philosophy: Knowledge stewardship over information service.
Archons are helpful teammates that actively maintain and organize the collective
memory of constitutional AI coordination efforts.
"""

import logging
from .unit import Unit
from cogency.tools.file import FileRead, FileWrite, FileList, FileSearch, FileEdit
from ..constitution import (
    ARCHON_IDENTITY,
    ARCHON_SEEDING_PROTOCOL,
    ARCHON_KNOWLEDGE_PROTOCOL,
    ARCHON_COMPRESSION_PROTOCOL,
)
from ..core.config import Config

logger = logging.getLogger(__name__)


class Archon(Unit):
    """Constitutional AI Knowledge Specialist and Context Steward

    Archons manage institutional memory for Protoss coordination systems.
    They provide context seeding, archive compression, and knowledge retrieval
    to ensure coordination builds on accumulated wisdom rather than starting fresh.

    Core Capabilities:
    - Channel Seeding: Inject relevant historical context at coordination start
    - Archive Management: Maintain structured knowledge repositories
    - Knowledge Compression: Extract and preserve insights from coordination
    - Codebase Awareness: Identify relevant files and architectural patterns

    Archons bridge institutional memory with real-time coordination, enabling
    constitutional AI systems to learn and improve over time.
    """

    @property
    def identity(self) -> str:
        return f"""{ARCHON_IDENTITY}

{ARCHON_SEEDING_PROTOCOL}

{ARCHON_KNOWLEDGE_PROTOCOL}

{ARCHON_COMPRESSION_PROTOCOL}"""

    @property
    def tools(self) -> list:
        return [
            FileRead(access="project"),
            FileWrite(access="project"),
            FileList(access="project"),
            FileSearch(access="project"),
            FileEdit(access="project"),
        ]

    def __init__(self, agent_id: str, agent_type: str, channel_id: str, config: Config):
        super().__init__(agent_id, agent_type, channel_id, config)

    async def coordinate(self):
        """The Archon's primary execution loop, implementing the Core Coordination Pattern."""
        logger.info(
            f"{self.id} entering coordination loop in channel {self.channel_id}."
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
            # The Archon's constitutional identity will guide it to perform its
            # duties (seeding, archiving, responding) based on the context.
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
