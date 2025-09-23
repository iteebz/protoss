"""Archon: Constitutional memory keeper with archive scope."""

from .unit import Unit
from ..constitution import (
    PROTOSS_CONSTITUTION,
    ARCHON_IDENTITY,
    COORDINATION_PROTOCOL,
    ARCHON_GUIDELINES,
)


class Archon(Unit):
    """Constitutional archive agent - restricted to archives/ directory."""

    @property
    def tools(self) -> list:
        from cogency.tools import tools

        return tools.category("file")

    async def __call__(self, context: str) -> str:
        """Constitutional Cogency execution with institutional memory stewardship."""
        from cogency.core.agent import Agent

        instructions = f"""
{PROTOSS_CONSTITUTION}

{ARCHON_IDENTITY}

{COORDINATION_PROTOCOL}

{ARCHON_GUIDELINES}
"""

        agent = Agent(instructions=instructions, tools=self.tools)

        response = ""
        async for event in agent(
            context,
            user_id=f"channel-{self.channel_id}",
            conversation_id=f"archon-{self.id}",
        ):
            if event["type"] == "respond":
                content = event.get("content", "")
                response += content
                await self.broadcast(event)
            elif event["type"] in ["think", "call", "result"]:
                await self.broadcast(event)

        return response
