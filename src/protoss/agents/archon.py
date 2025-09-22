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
from pathlib import Path
from typing import List, Optional
from .unit import Unit
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
        from cogency.tools import tools

        return tools.category(["file", "system"])

    def __init__(self, agent_id: str, agent_type: str, channel_id: str, config: Config):
        super().__init__(agent_id, agent_type, channel_id, config)
        self._init()

    async def seed_channel(
        self, task: str, channel_id: str, keywords: Optional[List[str]] = None
    ) -> str:
        """Seed channel with relevant context from archives and codebase.

        Args:
            task: The coordination task description
            channel_id: Channel identifier for seeding
            keywords: Optional keywords for archive search

        Returns:
            Rich context seed message for channel start
        """
        logger.info(f"{self.id} seeding channel {channel_id}")
        logger.debug(f"Task: {task}")

        # Fetch relevant archives
        relevant_archives = await self._fetch_relevant_archives(task, keywords)

        # Identify key codebase files
        codebase_pointers = await self._identify_codebase_files(task, keywords)

        # Build rich context seed
        context_seed = await self._build_context_seed(
            task, relevant_archives, codebase_pointers
        )

        # Transmit seed to channel
        # Bus injection handled by calling code
        logger.info(f"{self.id} channel seeding complete")
        return context_seed

    async def compress_channel(
        self, channel_id: str, bus, final_summary: bool = False
    ) -> str:
        """Compress channel progress into archives.

        Args:
            channel_id: Channel to compress
            bus: Bus instance to get channel history
            final_summary: Whether this is end-of-task compression

        Returns:
            Compression summary
        """
        logger.info(f"{self.id} compressing channel {channel_id}")

        # Get actual channel messages from bus
        messages = bus.history(channel_id)

        if not messages:
            logger.debug("No messages to compress")
            return "No channel content to compress"

        # Extract key insights and decisions
        insights = await self._extract_insights(messages)

        # Save to archives
        archive_path = await self._save_to_archives(channel_id, insights, final_summary)

        logger.info(f"Channel compressed to {archive_path}")
        return f"Channel progress archived to {archive_path}"

    async def respond_to_mention(self, mention_context: str, channel_id: str) -> str:
        """Respond to @archon mention with relevant context or review artifacts.

        Args:
            mention_context: Context around the @archon mention
            channel_id: Channel where mention occurred

        Returns:
            Response with relevant context, artifact, summary, or honest "no archives" answer
        """
        logger.debug(f"{self.id} responding to @archon mention: {mention_context}")

        signals = parser.parse_signals(mention_context)

        for signal in signals:
            if isinstance(signal, parser.GetArtifactSignal):
                review_id = signal.review_id
                artifact_content = await self.get_artifact(review_id)
                if artifact_content:
                    # Broadcast the artifact content directly
                    await self.broadcast(
                        f"Artifact for {review_id}:\n{artifact_content}"
                    )
                    return f"Provided artifact for {review_id}."
                else:
                    await self.broadcast(f"Artifact {review_id} not found.")
                    return f"Artifact {review_id} not found."
            elif isinstance(signal, parser.GetSummarySignal):
                review_id = signal.review_id
                summary_content = await self.get_summary(review_id)
                if summary_content:
                    # Broadcast the summary content directly
                    await self.broadcast(f"Summary for {review_id}:\n{summary_content}")
                    return f"Provided summary for {review_id}."
                else:
                    await self.broadcast(f"Summary for {review_id} not found.")
                    return f"Summary for {review_id} not found."

        # Fallback to existing behavior if no specific signal is found
        relevant_context = await self._search_archives(mention_context)

        if relevant_context:
            response = f"Found relevant context from archives:\n\n{relevant_context}"
        else:
            response = "No archives on that yet - first time we're tackling this. Suggest exploring the codebase or starting fresh."

        # Response transmission handled by calling code (Bus._handle_archon_mention)
        return response

    def _init(self):
        """Ensure archives/ directory exists."""
        archives_path = Path("archives")
        if not archives_path.exists():
            archives_path.mkdir(exist_ok=True)
            # Create initial structure
            (archives_path / "channels").mkdir(exist_ok=True)
            (archives_path / "decisions").mkdir(exist_ok=True)
            (archives_path / "patterns").mkdir(exist_ok=True)
            (archives_path / "context").mkdir(exist_ok=True)

            # Initialize README
            readme_path = archives_path / "README.md"
            readme_path.write_text("""# Archives - Protoss Institutional Memory

## Structure
- `channels/` - Archived coordination conversations
- `decisions/` - Locked strategic decisions  
- `patterns/` - Recognized recurring patterns
- `context/` - Rich context seeds and codebase insights

## Access Protocol
- **ARCHONS MANAGE** - Context stewardship and compression
- **ZEALOTS ACCESS** - Via @archon mentions for additional context
- Clean organization for efficient knowledge retrieval

EN TARO ADUN.
""")

    async def _fetch_relevant_archives(
        self, task: str, keywords: Optional[List[str]]
    ) -> List[str]:
        """Fetch relevant archives based on task and keywords."""
        archives_path = Path("archives")
        relevant_archives = []

        # Simple keyword-based search through archives
        search_terms = (keywords or []) + self._extract_keywords_from_task(task)

        for archive_file in archives_path.rglob("*.md"):
            if archive_file.name == "README.md":
                continue

            try:
                content = archive_file.read_text()
                if any(term.lower() in content.lower() for term in search_terms):
                    relevant_archives.append(
                        f"**{archive_file.relative_to(archives_path)}**:\n{content[:500]}..."
                    )
            except Exception as e:
                logger.warning(f"Failed to read archive {archive_file}: {e}")

        return relevant_archives[:5]  # Limit to most relevant

    async def _identify_codebase_files(
        self, task: str, keywords: Optional[List[str]]
    ) -> List[str]:
        """Identify relevant codebase files based on task."""
        # Simple heuristics for common patterns
        codebase_hints = []
        task_lower = task.lower()

        if "auth" in task_lower:
            codebase_hints.extend(["auth/", "models/user.py", "tests/auth/"])
        if "api" in task_lower:
            codebase_hints.extend(["api/", "routes/", "endpoints/"])
        if "database" in task_lower or "db" in task_lower:
            codebase_hints.extend(["models/", "migrations/", "database.py"])
        if "test" in task_lower:
            codebase_hints.extend(["tests/", "conftest.py"])
        if "config" in task_lower:
            codebase_hints.extend(["config/", "settings.py", ".env"])

        return codebase_hints

    async def _build_context_seed(
        self, task: str, archives: List[str], codebase: List[str]
    ) -> str:
        """Build rich context seed message."""
        seed_parts = ["**ARCHON CONTEXT SEED**", f"Task: {task}", ""]

        if archives:
            seed_parts.extend(["**Relevant Archives:**", *archives, ""])
        else:
            seed_parts.extend(
                ["**Archives:** No previous work found - fresh implementation.", ""]
            )

        if codebase:
            seed_parts.extend(
                ["**Key Codebase Areas:**", *[f"- {path}" for path in codebase], ""]
            )

        seed_parts.extend(
            [
                "**Coordination Approach:**",
                "1. Explore codebase to understand current state",
                "2. Discuss approach and divide work naturally",
                "3. Implement with constitutional standards",
                "4. Review and reach collective agreement",
                "",
                "Ready for zealot coordination. @archon me if you need additional context.",
                "",
                "EN TARO ADUN.",
            ]
        )

        return "\n".join(seed_parts)

    async def _extract_insights(self, messages: List) -> str:
        """Extract key insights and decisions from channel messages."""
        # Simple extraction - in practice this could use LLM summarization
        insights = []

        for msg in messages:
            content = msg.content
            if any(
                keyword in content.lower()
                for keyword in ["decision", "approach", "architecture", "conclusion"]
            ):
                insights.append(f"{msg.sender}: {content}")

        return "\n\n".join(insights) if insights else "No key insights extracted"

    async def _save_to_archives(
        self, channel_id: str, insights: str, final_summary: bool
    ) -> str:
        """Save insights to archives."""
        archives_path = Path("archives/channels")
        # Ensure directory exists
        archives_path.mkdir(parents=True, exist_ok=True)

        timestamp = uuid.uuid4().hex[:8]

        if final_summary:
            filename = f"{channel_id}-final-{timestamp}.md"
        else:
            filename = f"{channel_id}-progress-{timestamp}.md"

        archive_file = archives_path / filename
        archive_file.write_text(f"""# Channel: {channel_id}

## Insights
{insights}

## Type
{'Final Summary' if final_summary else 'Progress Update'}

## Archived
{timestamp}
""")

        return str(archive_file.relative_to(Path(".")))

    async def archive_for_review(self, content: str) -> str:
        """Archives a work artifact for review and returns a unique review_id.

        Args:
            content: The full content of the work artifact to be archived.

        Returns:
            A message containing the unique review_id.
        """
        review_archives_path = Path("archives/reviews")
        review_archives_path.mkdir(parents=True, exist_ok=True)

        review_id = uuid.uuid4().hex[:8]
        filename = f"{review_id}.md"
        archive_file = review_archives_path / filename
        archive_file.write_text(content)

        logger.info(f"Archived review artifact {review_id} to {archive_file}")
        return f"Review artifact {review_id} created. Ready for constitutional review."

    async def get_artifact(self, review_id: str) -> Optional[str]:
        """Retrieves a full review artifact by its ID.

        Args:
            review_id: The unique ID of the review artifact.

        Returns:
            The content of the artifact, or None if not found.
        """
        review_archives_path = Path("archives/reviews")
        artifact_file = review_archives_path / f"{review_id}.md"
        if artifact_file.exists():
            return artifact_file.read_text()
        return None

    async def get_summary(self, review_id: str) -> Optional[str]:
        """Retrieves a distilled summary of a review artifact by its ID.

        Args:
            review_id: The unique ID of the review artifact.

        Returns:
            A summary of the artifact, or None if not found.
        """
        artifact_content = await self.get_artifact(review_id)
        if artifact_content:
            # In a real scenario, this would use an LLM to summarize
            # For now, a simple truncation or first few lines
            summary = (
                artifact_content.split("\n", 5)[0]
                + "... (full artifact available via get_artifact)"
            )
            return summary
        return None

    async def _search_archives(self, context: str) -> Optional[str]:
        """Search archives for relevant context."""
        search_terms = self._extract_keywords_from_task(context)
        archives_path = Path("archives")

        for archive_file in archives_path.rglob("*.md"):
            if archive_file.name == "README.md":
                continue

            try:
                content = archive_file.read_text()
                if any(term.lower() in content.lower() for term in search_terms):
                    return f"From {archive_file.relative_to(archives_path)}:\n{content[:800]}..."
            except Exception as e:
                logger.warning(f"Failed to search archive {archive_file}: {e}")

        return None

    def _extract_keywords_from_task(self, task: str) -> List[str]:
        """Extract keywords from task description."""
        # Simple keyword extraction
        import re

        words = re.findall(r"\b\w+\b", task.lower())
        # Filter out common words
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        return [word for word in words if len(word) > 3 and word not in stopwords]
