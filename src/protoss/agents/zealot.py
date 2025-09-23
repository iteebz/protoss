"""Zealot: Constitutional AI agent with righteous conviction."""

from .unit import Unit
from ..constitution import (
    PROTOSS_CONSTITUTION,
    ZEALOT_IDENTITY,
    COORDINATION_PROTOCOL,
    ZEALOT_GUIDELINES,
)


class Zealot(Unit):
    """Constitutional AI agent - eliminates complexity, enforces principles."""

    @property
    def tools(self) -> list:
        from cogency.tools import tools

        return tools.category(["file", "system"])

    async def __call__(self, context: str) -> str:
        """Constitutional Cogency execution with emergence hierarchy."""
        from cogency.core.agent import Agent

        instructions = f"""
{PROTOSS_CONSTITUTION}

{ZEALOT_IDENTITY}

{COORDINATION_PROTOCOL}

{ZEALOT_GUIDELINES}
"""

        agent = Agent(instructions=instructions, tools=self.tools)

        response = ""
        async for event in agent(
            context,
            user_id=f"channel-{self.channel_id}",
            conversation_id=f"zealot-{self.id}",
        ):
            if event["type"] == "respond":
                content = event.get("content", "")
                response += content
                await self.broadcast(event)
            elif event["type"] in ["think", "call", "result"]:
                await self.broadcast(event)

        return response
