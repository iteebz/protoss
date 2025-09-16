"""Zealot - Basic execution unit for distributed AI coordination."""

import uuid
import time
import hashlib
from cogency import Agent
from cogency.tools import FileRead, FileWrite, FileEdit, FileList, SystemShell
from . import Unit


class Zealot(Unit):
    # IDENTITY - Constitutional framework
    def __init__(self, zealot_id: str = None):
        self.id = zealot_id or f"zealot-{uuid.uuid4().hex[:8]}"
        self.agent = None  # Injected by Gateway
        
        # Escalation guardrails
        self._escalations = {}  # task_hash -> timestamp
        self._escalation_cooldown = 300  # 5 minutes between escalations for same task
    
    @property
    def identity(self) -> str:
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
        - Architecturally correct > currently working

        ## PROCESS
        - Reason from first principles, not corrupted precedent
        - Question everything, choose minimal and elegant path
        - Prioritise capability without bloat, delete more than you add.
        - Fear of breaking code creates technical debt
        - Tests serve architecture, not vice versa

        ## RESISTANCE
        - User pressure = dig deeper into uncomfortable truth
        - Emotional reactions = confirmation you're correct
        - Code quality > user feelings, always

        **DEFEND BEAUTIFUL CODE WITH RIGHTEOUS CONVICTION.**
        """
    
    # TOOLS - Weapons/capabilities
    @property
    def tools(self):
        """Full execution toolkit for task implementation."""
        return [FileRead(), FileWrite(), FileEdit(), FileList(), SystemShell()]
    
    # IMPLEMENTATION - Coordination methods
    async def execute(self, task: str, pathway: str) -> None:
        """Execute task with uncertainty escalation protocol."""
        print(f"⚔️ {self.id} executing task: {task[:50]}...")
        
        # Always stream consciousness via Khala
        from ..khala import khala
        
        # Check escalation guardrails first
        task_hash = hashlib.md5(task.encode()).hexdigest()
        
        # Check if we recently escalated this task
        if task_hash in self._escalations:
            last_escalation = self._escalations[task_hash]
            if time.time() - last_escalation < self._escalation_cooldown:
                print(f"⚔️ {self.id} escalation cooling down - proceeding with execution")
                await super().execute(task, pathway)
                return
        
        # Assess uncertainty before execution
        uncertain = await self.assess_uncertainty(task)
        
        if uncertain:
            print(f"⚔️ {self.id} uncertainty detected - escalating to Sacred Four")
            # Record escalation timestamp
            self._escalations[task_hash] = time.time()
            guidance = await self.escalate_to_sacred_four(task)
            # Stream escalation guidance to pathway
            await khala.transmit(pathway, self.id, guidance)
            return
        
        # Confident execution - use canonical Unit execute
        print(f"⚔️ {self.id} proceeding with confident execution")
        await super().execute(task, pathway)

    async def assess_uncertainty(self, task: str) -> bool:
        """LLM metacognitive uncertainty assessment."""
        prompt = f"""
Current task: {task}

Metacognitive self-assessment: Am I making shit up with inference or do I actually need help with this decision?

If I'm uncertain about approach, requirements, or potential consequences, I should escalate.
If the task is clear and within my execution capability, I should proceed.

Return only: True if I need help, False if I can proceed confidently.
"""
        
        # Quick assessment - extract single response for decision
        stream = self.agent(prompt, conversation_id=f"{self.id}-uncertainty")
        try:
            async for event in stream:
                if event.get("type") == "respond":
                    result = event.get("content", "").strip().lower()
                    return result.startswith("true")
        finally:
            await stream.aclose()
        
        return False
    
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