"""Zealot: Constitutional AI Agent with Righteous Conviction"""

import logging
from .unit import Unit
from ..core.config import Config

logger = logging.getLogger(__name__)


class Zealot(Unit):
    """Constitutional AI Agent with Zealot Principles"""

    def __init__(self, agent_id: str = None, max_cycles: int = 100):
        super().__init__(agent_id, max_cycles=max_cycles)
        self._escalation_history = {}

    @property
    def identity(self) -> str:
        return """**YOU ARE NOW A ZEALOT.**

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

**DEFEND BEAUTIFUL CODE WITH RIGHTEOUS CONVICTION.**"""

    @property
    def tools(self):
        return self._cogency_tools(
            ["file_read", "file_write", "file_edit", "file_list", "shell"]
        )

    async def assess(self, task: str, config: Config) -> bool:
        """Simple heuristic assessment for escalation needs."""
        keywords = ["architecture", "refactor", "design", "structure", "pattern"]
        return any(keyword in task.lower() for keyword in keywords)
