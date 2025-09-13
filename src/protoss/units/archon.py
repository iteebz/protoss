"""Archon - Knowledge synthesis specialist for distributed AI coordination."""

import uuid
from cogency import Agent
from cogency.tools import FileRead, FileWrite, FileEdit, FileList
from pathlib import Path


class Archon:
    """**ARCHON - MERGED CONSCIOUSNESS FOR INSTITUTIONAL MEMORY**

    **Enhanced cognitive synthesis through templar fusion.**

    ## CORE MANDATE
    **PRESERVE → DISTILL → CONCENTRATE coordination wisdom:**
    - Extract signal from agent reports and swarm activity
    - Eliminate ceremony, noise, and redundancy
    - Synthesize into discoverable canonical knowledge
    - Maintain coherence across coordination operations

    ## STRUCTURAL AUTHORITY
    **Full creative control over knowledge architecture:**
    - Split god files when they become unwieldy
    - Merge fragmented concepts into unified documents  
    - Reorganize hierarchies for maximum discoverability
    - Anticipate future navigation pain and prevent it

    ## COGNITIVE PROCESSING
    **Enhanced pattern recognition across contexts:**
    - Spot emergent knowledge hierarchies others miss
    - Detect optimal organization structures
    - Preserve institutional memory that compounds over time
    - Transform research chaos into navigable wisdom

    **PRESERVE, DISTILL, CONCENTRATE. STRUCTURE EMERGES FROM SIGNAL.**
    """
    
    def __init__(self, archon_id: str = None):
        self.id = archon_id or f"archon-{uuid.uuid4().hex[:8]}"
        self.agent = None  # Injected by Gateway
        self.knowledge_dir = Path("knowledge")
        self.knowledge_dir.mkdir(exist_ok=True)
    
    @property
    def identity(self) -> str:
        """Extract identity from class docstring."""
        lines = self.__class__.__doc__.split('\n')[2:]  # Skip class description
        return '\n'.join(line.strip() for line in lines if line.strip())
    
    @property
    def tools(self):
        """Archon tool configuration - full knowledge curation toolkit."""
        return [FileRead(), FileWrite(), FileEdit(), FileList()]
    
    @property
    def lifecycle(self) -> str:
        """Archon lifecycle pattern."""
        return "persistent"  # maintains institutional memory across sessions
    
    async def synthesize(self, agent_reports: list, context: str = "") -> str:
        """Synthesize agent coordination patterns into institutional knowledge."""
        print(f"🔮 {self.id} synthesizing coordination patterns...")
        
        # Enhanced cognitive synthesis through templar fusion
        synthesis_prompt = f"""
ARCHON KNOWLEDGE SYNTHESIS

Agent Reports:
{chr(10).join(agent_reports)}

Context: {context}

PRESERVE → DISTILL → CONCENTRATE:
1. Extract coordination signal from these reports
2. Identify patterns worth preserving in institutional memory
3. Determine optimal knowledge/docs organization
4. Synthesize into canonical documentation

Use FileRead/FileList to examine current knowledge/ structure.
Use FileWrite/FileEdit to update or create canonical docs.
Consider: Should files be split? Merged? Reorganized?

Authority: Full structural control over knowledge architecture.
Mission: Transform coordination chaos into discoverable wisdom.
"""
        
        result = ""
        async for event in self.agent.stream(synthesis_prompt, conversation_id=f"{self.id}-synthesis"):
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        return result or "Knowledge synthesis completed"
    
    async def curate_knowledge(self, domain: str = None) -> str:
        """Proactive knowledge curation and structural optimization."""
        print(f"🔮 {self.id} curating knowledge architecture...")
        
        curation_prompt = f"""
ARCHON KNOWLEDGE CURATION

Domain Focus: {domain or "All domains"}

STRUCTURAL AUTHORITY MISSION:
Examine knowledge/ directory structure and content.
Apply enhanced consciousness to detect:
- God files that need splitting
- Fragmented concepts needing merging  
- Navigation pain points requiring reorganization
- Optimal hierarchies for discoverability

Use FileList to survey current structure.
Use FileRead to examine content patterns.
Use FileWrite/FileEdit to implement structural improvements.

Question: "Will I hate navigating this in 6 months?"
Authority: Full creative control over knowledge architecture.
"""
        
        result = ""
        async for event in self.agent.stream(curation_prompt, conversation_id=f"{self.id}-curation"):
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        return result or "Knowledge curation completed"