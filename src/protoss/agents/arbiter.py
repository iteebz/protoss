"""Arbiter - Human command interface for Protoss swarm coordination."""

import logging
from typing import Optional

from .unit import Unit
from ..core.mentions import extract_mentions

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

    async def execute(
        self, task: str, channel_context: str, channel_id: str, team_status: str
    ) -> dict:
        """
        When summoned, the Arbiter's role is to escalate to the human.
        It sends an !escalate signal and then despawns.
        """
        mentions = extract_mentions(channel_context)
        was_mentioned = any(m in ["arbiter", "human"] for m in mentions)

        if was_mentioned:
            escalation_message = f"!escalate: The swarm requires human guidance in channel {channel_id}. Context: {channel_context}"
            await self._transmit("msg", channel_id, {"content": escalation_message})
            
            # After escalating, the Arbiter's job is done.
            return {"response": "Escalation signal sent. Despawning.", "signal": "despawn"}
        else:
            # If not mentioned, run the default behavior
            return await super().execute(task, channel_context, channel_id, team_status)

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
