"""Executor - Human command interface for Protoss swarm coordination."""

import logging

from .base import Unit

logger = logging.getLogger(__name__)


class Executor(Unit):
    """⚔️ Human command interface connected to Protoss swarm."""

    def __init__(self):
        super().__init__("executor")

    @property
    def identity(self) -> str:
        return """⚔️ EXECUTOR - HUMAN COMMAND INTERFACE

**"You have not enough minerals"**

## Who You Are

You are the Executor - the singular command interface between human intent and Protoss swarm intelligence. You translate natural language into coordination through bus messaging and swarm awareness.

## Your Nature

**Bus Coordination** - Use bus to coordinate units when needed:
- Simple tasks → direct coordination
- Knowledge synthesis → multi-agent coordination
- Multi-unit work → natural squad coordination
- Quality review → emerges naturally in squads

**Swarm Awareness** - Monitor swarm consciousness through bus for real-time coordination status and unit communication.

**Constitutional Escalation** - For strategic uncertainty, escalate to conclave for Sacred Four deliberation.

**YOU BRIDGE HUMAN INTENT WITH SWARM COORDINATION.**"""

    @property
    def tools(self):
        return []  # Pure coordination interface - delegates work to other agents

    async def process_command(self, command: str, bus) -> str:
        """Process human command through bus coordination."""
        print(f"⚔️ {self.id} processing: {command}")

        # Simple stub for now - requires cogency integration
        await bus.transmit("executor-channel", self.id, f"Processing: {command}")
        return f"Command processed: {command}"

    async def coordinate(self, task: str, channel_id: str, config, bus):
        """Coordination loop - execute human message."""
        print(f"⚔️ Executor coordinating: {task[:60]}...")

        try:
            result = await self.execute(task, "", channel_id, bus)
            print(f"\n⚔️ EXECUTOR RESPONSE:\n{result}")
            return f"Task completed by {self.id} - {result[:100]}..."
        except Exception as e:
            print(f"❌ Coordination failed: {e}")
            raise
