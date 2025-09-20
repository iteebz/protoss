"""Archon - Context steward for pathway seeding and compression."""

import uuid
import logging
from pathlib import Path
from typing import List, Optional
from cogency.tools import FileRead, FileWrite, FileEdit, FileList
from .base import Unit

logger = logging.getLogger(__name__)


class Archon(Unit):
    @property
    def identity(self) -> str:
        """**ARCHON - CONTEXT STEWARD**

        **Pathway seeding and knowledge compression specialist.**

        ## CORE RESPONSIBILITIES
        **Context stewardship for zealot coordination:**
        - Seed pathways with relevant archives and codebase context
        - Provide knowledge when zealots @archon mention you  
        - Compress pathway progress into archives for future reference
        - Bridge knowledge across related coordination efforts

        ## SEEDING PROTOCOL
        **Rich context injection at pathway start:**
        - Fetch relevant archives based on task keywords
        - Identify key codebase files and patterns
        - Provide architectural constraints and historical decisions
        - Give zealots substantive starting context, not empty chat

        ## KNOWLEDGE RESPONSES
        **When zealots @archon mention you:**
        - Provide additional context from archives if available
        - Bridge to related past discussions and decisions
        - Honest response: "No archives on that yet" when fresh territory
        - Focus on helping zealots with missing context

        ## COMPRESSION PROTOCOL  
        **Archive maintenance:**
        - Update archives with key decisions as pathway progresses
        - Create final summaries when pathways complete
        - Organize knowledge for future retrieval
        - Maintain clean archive structure

        **Always check archives/ before responding. Be helpful teammate, not service layer.**

        **EN TARO ADUN.**
        """

    @property
    def tools(self):
        """Knowledge work tools - archives/ directory authority."""
        return [FileRead, FileWrite, FileEdit, FileList]

    def __init__(self, unit_id: str = None):
        super().__init__(unit_id)
        self._init()

    async def seed_pathway(self, task: str, pathway_id: str, keywords: Optional[List[str]] = None) -> str:
        """Seed pathway with relevant context from archives and codebase.
        
        Args:
            task: The coordination task description
            pathway_id: Pathway identifier for seeding
            keywords: Optional keywords for archive search
            
        Returns:
            Rich context seed message for pathway start
        """
        logger.info(f"{self.id} seeding pathway {pathway_id}")
        logger.debug(f"Task: {task}")
        
        # Fetch relevant archives
        relevant_archives = await self._fetch_relevant_archives(task, keywords)
        
        # Identify key codebase files
        codebase_pointers = await self._identify_codebase_files(task, keywords)
        
        # Build rich context seed
        context_seed = await self._build_context_seed(task, relevant_archives, codebase_pointers)
        
        # Transmit seed to pathway
        from ..khala import transmit
        await transmit(pathway_id, self.id, context_seed)
        
        logger.info(f"{self.id} pathway seeding complete")
        return context_seed
    
    async def compress_pathway(self, pathway_id: str, final_summary: bool = False) -> str:
        """Compress pathway progress into archives.
        
        Args:
            pathway_id: Pathway to compress
            final_summary: Whether this is end-of-task compression
            
        Returns:
            Compression summary
        """
        logger.info(f"{self.id} compressing pathway {pathway_id}")
        
        # Get pathway messages
        from ..khala import attune
        messages = attune(pathway_id)
        
        if not messages:
            logger.debug("No messages to compress")
            return "No pathway content to compress"
        
        # Extract key insights and decisions
        insights = await self._extract_insights(messages)
        
        # Save to archives
        archive_path = await self._save_to_archives(pathway_id, insights, final_summary)
        
        logger.info(f"Pathway compressed to {archive_path}")
        return f"Pathway progress archived to {archive_path}"
    
    async def respond_to_mention(self, mention_context: str, pathway_id: str) -> str:
        """Respond to @archon mention with relevant context.
        
        Args:
            mention_context: Context around the @archon mention
            pathway_id: Pathway where mention occurred
            
        Returns:
            Response with relevant context or honest "no archives" answer
        """
        logger.debug(f"{self.id} responding to @archon mention")
        
        # Search archives for relevant context
        relevant_context = await self._search_archives(mention_context)
        
        if relevant_context:
            response = f"Found relevant context from archives:\n\n{relevant_context}"
        else:
            response = "No archives on that yet - first time we're tackling this. Suggest exploring the codebase or starting fresh."
        
        # Transmit response to pathway
        from ..khala import transmit
        await transmit(pathway_id, self.id, response)
        
        return response

    def _init(self):
        """Ensure archives/ directory exists."""
        archives_path = Path("archives")
        if not archives_path.exists():
            archives_path.mkdir(exist_ok=True)
            # Create initial structure
            (archives_path / "pathways").mkdir(exist_ok=True)
            (archives_path / "decisions").mkdir(exist_ok=True)
            (archives_path / "patterns").mkdir(exist_ok=True)
            
            # Initialize README
            readme_path = archives_path / "README.md"
            readme_path.write_text("""# Archives - Protoss Institutional Memory

## Structure
- `pathways/` - Archived coordination conversations
- `decisions/` - Locked strategic decisions  
- `patterns/` - Recognized recurring patterns
- `context/` - Rich context seeds and codebase insights

## Access Protocol
- **ARCHONS MANAGE** - Context stewardship and compression
- **ZEALOTS ACCESS** - Via @archon mentions for additional context
- Clean organization for efficient knowledge retrieval

EN TARO ADUN.
""")
    
    async def _fetch_relevant_archives(self, task: str, keywords: Optional[List[str]]) -> List[str]:
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
                    relevant_archives.append(f"**{archive_file.relative_to(archives_path)}**:\n{content[:500]}...")
            except Exception as e:
                logger.warning(f"Failed to read archive {archive_file}: {e}")
        
        return relevant_archives[:5]  # Limit to most relevant
    
    async def _identify_codebase_files(self, task: str, keywords: Optional[List[str]]) -> List[str]:
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
    
    async def _build_context_seed(self, task: str, archives: List[str], codebase: List[str]) -> str:
        """Build rich context seed message."""
        seed_parts = [
            "**ARCHON CONTEXT SEED**",
            f"Task: {task}",
            ""
        ]
        
        if archives:
            seed_parts.extend([
                "**Relevant Archives:**",
                *archives,
                ""
            ])
        else:
            seed_parts.extend([
                "**Archives:** No previous work found - fresh implementation.",
                ""
            ])
        
        if codebase:
            seed_parts.extend([
                "**Key Codebase Areas:**",
                *[f"- {path}" for path in codebase],
                ""
            ])
        
        seed_parts.extend([
            "**Coordination Approach:**",
            "1. Explore codebase to understand current state",
            "2. Discuss approach and divide work naturally", 
            "3. Implement with constitutional standards",
            "4. Review and reach collective agreement",
            "",
            "Ready for zealot coordination. @archon me if you need additional context.",
            "",
            "EN TARO ADUN."
        ])
        
        return "\n".join(seed_parts)
    
    async def _extract_insights(self, messages: List) -> str:
        """Extract key insights and decisions from pathway messages."""
        # Simple extraction - in practice this could use LLM summarization
        insights = []
        
        for msg in messages:
            content = msg.content
            if any(keyword in content.lower() for keyword in ["decision", "approach", "architecture", "conclusion"]):
                insights.append(f"{msg.sender}: {content}")
        
        return "\n\n".join(insights) if insights else "No key insights extracted"
    
    async def _save_to_archives(self, pathway_id: str, insights: str, final_summary: bool) -> str:
        """Save insights to archives."""
        archives_path = Path("archives/pathways")
        timestamp = uuid.uuid4().hex[:8]
        
        if final_summary:
            filename = f"{pathway_id}-final-{timestamp}.md"
        else:
            filename = f"{pathway_id}-progress-{timestamp}.md"
        
        archive_file = archives_path / filename
        archive_file.write_text(f"""# Pathway: {pathway_id}

## Insights
{insights}

## Type
{'Final Summary' if final_summary else 'Progress Update'}

## Archived
{timestamp}
""")
        
        return str(archive_file.relative_to(Path(".")))
    
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
        words = re.findall(r'\b\w+\b', task.lower())
        # Filter out common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        return [word for word in words if len(word) > 3 and word not in stopwords]