"""Zealot: Constitutional AI Agent with Righteous Conviction"""

import logging
from .unit import Unit
from ..core.config import Config
from ..constitution import ZEALOT_IDENTITY

logger = logging.getLogger(__name__)


class Zealot(Unit):
    """Constitutional AI Agent with Zealot Principles"""

    def __init__(self, agent_id: str = None, max_cycles: int = 100):
        super().__init__(agent_id, max_cycles=max_cycles)
        self._escalation_history = {}

    @property
    def identity(self) -> str:
        return ZEALOT_IDENTITY

    @property
    def tools(self):
        return self._cogency_tools(
            ["file_read", "file_write", "file_edit", "file_list", "shell"]
        )

    async def assess(self, task: str, config: Config) -> bool:
        """Simple heuristic assessment for escalation needs."""
        keywords = ["architecture", "refactor", "design", "structure", "pattern"]
        return any(keyword in task.lower() for keyword in keywords)
