"""Zealot - Constitutional execution unit for coordination tasks."""

import uuid
import time
import hashlib
import logging
from cogency.tools import FileRead, FileWrite, FileEdit, FileList, SystemShell
from .base import Unit

logger = logging.getLogger(__name__)


class Zealot(Unit):
    """Constitutional execution unit with zealot principles.
    
    Zealots apply constitutional standards to coordination tasks,
    pushing back on overengineering and defending code quality.
    """
    
    def __init__(self, unit_id: str = None):
        super().__init__(unit_id)
        
        # Escalation guardrails to prevent spam
        self._escalation_history = {}  # task_hash -> timestamp
        
    @property 
    def cooldown(self) -> int:
        """Get escalation cooldown from config."""
        from ..config import get_config
        return get_config().cooldown

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

    # METHODS - Constitutional assessment and escalation
    async def assess(self, task: str) -> bool:
        """Assess whether task requires Sacred Four guidance."""
        logger.debug(f"{self.id} assessing uncertainty for task")
        
        # Check escalation cooldown first
        task_hash = hashlib.md5(task.encode()).hexdigest()
        if self._is_escalation_on_cooldown(task_hash):
            logger.debug(f"{self.id} escalation on cooldown, proceeding with task")
            return False
        
        assessment_prompt = f"""
Current coordination context: {task}

Constitutional assessment: Does this coordination task require Sacred Four deliberation?

Consider:
- Are there complex architectural decisions beyond zealot scope?
- Does this involve constitutional principles that need deliberation?
- Is this a simple implementation task within zealot capabilities?

Return only: True if I need Sacred Four guidance, False if I can proceed with coordination.
"""
        
        # Create temporary agent for assessment
        from cogency import Agent
        assessment_agent = Agent(
            instructions=self.identity,
            conversation_id=f"{self.id}-assessment-{uuid.uuid4().hex[:8]}"
        )
        
        try:
            stream = assessment_agent(assessment_prompt)
            async for event in stream:
                if event.get("type") == "respond":
                    result = event.get("content", "").strip().lower()
                    needs_escalation = result.startswith("true")
                    logger.debug(f"{self.id} uncertainty assessment: {'ESCALATE' if needs_escalation else 'PROCEED'}")
                    return needs_escalation
        except Exception as e:
            logger.warning(f"{self.id} assessment failed: {e}")
            return False  # Default to proceeding if assessment fails
        finally:
            await stream.aclose()

        return False
    
    def _is_escalation_on_cooldown(self, task_hash: str) -> bool:
        """Check if escalation is on cooldown for this task."""
        if task_hash not in self._escalation_history:
            return False
        
        last_escalation = self._escalation_history[task_hash]
        elapsed = time.time() - last_escalation
        return elapsed < self.cooldown


    async def escalate(self, task: str) -> str:
        """Escalate task for strategic consultation.
        
        Args:
            task: The coordination task requiring strategic input
            
        Returns:
            Strategic perspectives or error message
        """
        from ..conclave import consult

        # Record escalation timestamp
        task_hash = hashlib.md5(task.encode()).hexdigest()
        self._escalation_history[task_hash] = time.time()

        try:
            # Format strategic question
            strategic_question = f"""ZEALOT ESCALATION: {task}
            
Zealot {self.id} needs strategic perspectives on this coordination challenge.
What are the architectural trade-offs and different approaches to consider?"""

            logger.info(f"{self.id} requesting strategic consultation")
            perspectives = await consult(strategic_question)

            return f"""STRATEGIC PERSPECTIVES RECEIVED
            
Task: {task}
Zealot: {self.id}
Status: Strategic consultation provided

{perspectives}"""

        except Exception as e:
            logger.error(f"{self.id} strategic consultation failed: {e}")
            return f"""CONSULTATION FAILED: {e}
            
Task: {task}
Zealot: {self.id}
Status: Strategic consultation unavailable

Proceeding with coordination using available information."""
