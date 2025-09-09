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
        self.agent = Agent(instructions=self.identity, tools=self.tools)
    
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
        return "ephemeral"  # spawn → execute → die
    
    async def execute(self, task: str) -> str:
        """Execute task and return result."""
        result = ""
        async for event in self.agent.stream(task, conversation_id=self.id):
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        return result or "Task completed"