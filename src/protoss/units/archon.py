"""Archon - Knowledge synthesis specialist for distributed AI coordination."""

import uuid
from cogency import Agent
from . import Unit
from cogency.tools import FileRead, FileWrite, FileEdit, FileList
from pathlib import Path


class Archon(Unit):
    
    @property
    def identity(self) -> str:
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
    
    @property
    def tools(self):
        """Archon tools: Knowledge curation and synthesis."""
        return [FileRead(), FileWrite(), FileEdit(), FileList()]
    
    def __init__(self, archon_id: str = None):
        self.id = archon_id or f"archon-{uuid.uuid4().hex[:8]}"
        self.agent = None  # Injected by Gateway
    
    async def execute(self, task: str, pathway: str) -> None:
        """Execute knowledge synthesis."""
        print(f"🔮 {self.id} synthesizing: {task[:50]}...")
        await super().execute(task, pathway)
    
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
        stream = self.agent(curation_prompt, conversation_id=f"{self.id}-curation")
        try:
            async for event in stream:
                if event.get("type") == "respond":
                    result = event.get("content", "")
                    break
        finally:
            await stream.aclose()
        return result or "Knowledge curation completed"