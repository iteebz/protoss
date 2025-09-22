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
import uuid
from .unit import Unit
from cogency.tools.file import FileRead, FileWrite, FileList, FileSearch, FileEdit
from ..constitution import (
    ARCHON_IDENTITY,
    ARCHON_SEEDING_PROTOCOL,
    ARCHON_KNOWLEDGE_PROTOCOL,
    ARCHON_COMPRESSION_PROTOCOL,
)
from ..core.config import Config
from ..core import parser  # Corrected parser import

logger = logging.getLogger(__name__)


class Archon(Unit):
    """Constitutional AI Knowledge Specialist and Context Steward

    Archons manage institutional memory for Protoss coordination systems.
    They provide context seeding, archive compression, and knowledge retrieval
    to ensure coordination builds on accumulated wisdom rather than starting fresh.

    Core Capabilities:
    - Channel Seeding: Inject relevant historical context at coordination start
    - Archive Management: Maintain structured knowledge repositories
    - Mention Response: Provide context when zealots @archon for information
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

    async def seed_channel(
        self, task: str, channel_id: str, keywords=None
    ) -> str:
        """Seed channel with relevant context from archives and codebase."""
        logger.info(f"{self.id} seeding channel {channel_id}")
        return await super().__call__(f"Search archives/ for relevant context to seed coordination on: {task}")

    async def compress_channel(
        self, channel_id: str, bus, final_summary: bool = False
    ) -> str:
        """Compress channel progress into archives."""
        logger.info(f"{self.id} compressing channel {channel_id}")
        
        messages = bus.history(channel_id)
        if not messages:
            return "No channel content to compress"
            
        message_content = "\n".join([f"{msg.sender}: {msg.content}" for msg in messages])
        compression_type = "final summary" if final_summary else "progress update"
        
        return await super().__call__(f"Extract key insights from this {compression_type} and save to archives/channels/{channel_id}-{compression_type}.md:\n\n{message_content}")

    async def respond_to_mention(self, mention_context: str, channel_id: str) -> str:
        """Respond to @archon mention with relevant context."""
        logger.debug(f"{self.id} responding to @archon mention: {mention_context}")
        return await super().__call__(f"Search archives/ for context on: {mention_context}")

    async def archive_for_review(self, content: str) -> str:
        """Archives a work artifact for review and returns a unique review_id."""
        review_id = uuid.uuid4().hex[:8]
        return await super().__call__(f"Save this content to archives/reviews/{review_id}.md:\n\n{content}\n\nThen respond with: Review artifact {review_id} created. Ready for constitutional review.")

    async def get_artifact(self, review_id: str) -> str:
        """Retrieves a full review artifact by its ID."""
        return await super().__call__(f"Read the full content of archives/reviews/{review_id}.md")

    async def get_summary(self, review_id: str) -> str:
        """Retrieves a distilled summary of a review artifact by its ID."""
        return await super().__call__(f"Read archives/reviews/{review_id}.md and provide a concise summary")