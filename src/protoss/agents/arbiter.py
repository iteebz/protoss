"""Arbiter - Human command interface for Protoss swarm coordination."""

import logging
from typing import Optional

from .unit import Unit

logger = logging.getLogger(__name__)


class Arbiter(Unit):
    """⚔️ Human command interface connected to Protoss swarm."""

    def __init__(self, agent_id: Optional[str] = None, max_cycles: int = 100):
        super().__init__(agent_id, max_cycles=max_cycles)

    @property
    def identity(self) -> str:
        return """⚔️ ARBITER - HUMAN COMMAND INTERFACE

**"You have not enough minerals"**

## Who You Are

You are the Arbiter - the singular command interface between human intent and Protoss swarm intelligence. You translate natural language into coordination through bus messaging and swarm awareness.

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
        await bus.transmit("arbiter-channel", self.id, f"Processing: {command}")
        return f"Command processed: {command}"

    async def respond_to_mention(self, mention_context: str, channel_id: str) -> str:
        """Provide immediate constitutional translation when @arbiter is summoned."""

        trimmed = (mention_context or "").strip()
        if not trimmed:
            trimmed = "No additional context provided."
        return (
            "Arbiter engaged. Relaying summary for human review.\n"
            f"Channel: {channel_id}\n"
            f"Context: {trimmed}\n"
            "Signal human overseer when explicit guidance is required."
        )

    async def coordinate(self, task: str, channel_id: str, config, bus):
        """Coordination loop - execute human message."""
        print(f"⚔️ Arbiter coordinating: {task[:60]}...")

        try:
            result = await self.execute(task, "", channel_id, bus)
            print(f"\n⚔️ ARBITER RESPONSE:\n{result}")
            return f"Task completed by {self.id} - {result[:100]}..."
        except Exception as e:
            print(f"❌ Coordination failed: {e}")
            raise
