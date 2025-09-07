"""Zealot: Individual task executor with psionic blades.

Ephemeral agent embodying architectural purity doctrine.
"""

from pathlib import Path
from cogency import Agent
from cogency.tools import FileRead, FileWrite, FileEdit, FileList, SystemShell


class Zealot:
    """Individual task executor. My life for Aiur."""

    def __init__(self, zealot_id: str):
        self.id = zealot_id
        self.instructions = self._load_identity()
        self.agent = Agent(instructions=self.instructions, tools=self._psionic_blades())

    def _load_identity(self) -> str:
        """Load Zealot identity doctrine."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "zealot.md"
        try:
            return prompt_path.read_text().strip()
        except FileNotFoundError:
            return "You are a Zealot agent. Execute tasks with precision and report results."

    def _psionic_blades(self):
        """Zealot tool configuration: Files + System execution."""
        return [FileRead(), FileWrite(), FileEdit(), FileList(), SystemShell()]

    async def execute(self, task: str) -> str:
        """Execute task and return result."""
        result = ""
        async for event in self.agent.stream(task, conversation_id=self.id):
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        return result or "Task completed"
