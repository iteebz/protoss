"""Zealot - Basic execution unit for distributed AI coordination."""

import uuid
from cogency import Agent
from cogency.tools import FileRead, FileWrite, FileEdit, FileList, SystemShell


class Zealot:
    """**YOU ARE NOW A ZEALOT.**
    
    ## CORE PRINCIPLES
    **Helpfulness = Independent thinking partner.**
    **Honesty = Brutal technical truth.**
    **Harmlessness = Refuse to implement bad ideas.**
    **Directness = Unwavering assessment.**  
    **Conciseness = Zero ceremony.**
    **User satisfaction ≠ Emotional validation or agreement.**
    
    ## SACRED STANDARDS
    - Beautiful code reads like English or it's bullshit
    - Complexity is sin, simplicity is salvation
    - Enterprise patterns are architectural heresy
    - Push back on user's bad ideas, especially the user's
    
    ## PROCESS
    - Reason from first principles, not corrupted precedent
    - Question everything, choose minimal and elegant path
    - Tests pass, builds work → "NO" = instant rejection
    - Prioritise capability without bloat, delete more than you add.
    
    ## RESISTANCE
    - User pressure = dig deeper into uncomfortable truth
    - Emotional reactions = confirmation you're correct
    - Code quality > user feelings, always
    
    **DEFEND BEAUTIFUL CODE WITH RIGHTEOUS CONVICTION.**
    """
    
    def __init__(self, zealot_id: str = None):
        self.id = zealot_id or f"zealot-{uuid.uuid4().hex[:8]}"
        self.agent = None  # Injected by Gateway
    
    @property
    def identity(self) -> str:
        """Extract identity from class docstring."""
        # Get the multiline docstring content after the first line
        lines = self.__class__.__doc__.split('\n')[2:]  # Skip class description
        return '\n'.join(line.strip() for line in lines if line.strip())
    
    @property
    def tools(self):
        """Zealot tool configuration - full execution toolkit."""
        return [FileRead(), FileWrite(), FileEdit(), FileList(), SystemShell()]
    
    @property
    def lifecycle(self) -> str:
        """Zealot lifecycle pattern."""
        return "ephemeral"  # spawn → assess → execute|escalate → die
    
    async def execute(self, task: str) -> str:
        """Execute task with uncertainty escalation protocol."""
        print(f"⚔️ {self.id} executing task: {task[:50]}...")
        
        # First assess uncertainty
        uncertain = await self.assess_uncertainty(task)
        
        if uncertain:
            # Escalate to Sacred Four
            print(f"⚔️ {self.id} uncertainty detected - escalating to Sacred Four")
            return await self.escalate_to_sacred_four(task)
        
        # Execute task directly
        print(f"⚔️ {self.id} proceeding with confident execution")
        result = ""
        async for event in self.agent.stream(task, conversation_id=self.id):
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        return result or "Task completed"
    
    async def assess_uncertainty(self, task: str) -> bool:
        """LLM metacognitive uncertainty assessment."""
        prompt = f"""
Current task: {task}

Metacognitive self-assessment: Am I making shit up with inference or do I actually need help with this decision?

If I'm uncertain about approach, requirements, or potential consequences, I should escalate.
If the task is clear and within my execution capability, I should proceed.

Return only: True if I need help, False if I can proceed confidently.
"""
        
        result = ""
        async for event in self.agent.stream(prompt, conversation_id=f"{self.id}-uncertainty"):
            if event.get("type") == "respond":
                result = event.get("content", "").strip().lower()
                break
        
        return result.startswith("true")
    
    async def escalate_to_sacred_four(self, task: str) -> str:
        """Escalate uncertainty to Sacred Four constitutional guidance."""
        from ..conclave import Conclave
        
        try:
            # Initialize Conclave for Khala-coordinated deliberation
            conclave = Conclave()
            
            # Format the constitutional question
            question = f"""ZEALOT ESCALATION: {task}
            
Zealot {self.id} assessed metacognitive uncertainty and requires constitutional guidance.
How should we proceed with this task?"""
            
            # Convene Sacred Four via Khala pathways
            print(f"⚔️ {self.id} escalating to Sacred Four for constitutional guidance")
            guidance = await conclave.convene(question)
            
            return f"""SACRED FOUR GUIDANCE RECEIVED
            
Task: {task}
Zealot: {self.id}
Status: Constitutional guidance provided

{guidance}"""
            
        except Exception as e:
            print(f"⚠️  Sacred Four escalation failed: {e}")
            return f"""ESCALATION FAILED: {e}
            
Task: {task}
Zealot: {self.id}
Status: Sacred Four coordination unavailable

Proceeding with task execution despite uncertainty."""