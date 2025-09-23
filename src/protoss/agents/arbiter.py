"""Arbiter: Constitutional mediator and dispute resolution specialist."""

from .unit import Unit
from ..constitution import (
    PROTOSS_CONSTITUTION,
    ARBITER_IDENTITY,
    COORDINATION_PROTOCOL,
    ARBITER_GUIDELINES,
)


class Arbiter(Unit):
    """Constitutional arbiter - mediates disputes and ensures constitutional adherence."""

    @property
    def tools(self) -> list:
        from cogency.tools import tools

        return tools.category(["file", "system"])

    async def __call__(self, context: str) -> str:
        """Constitutional Cogency execution with human-swarm translation."""
        from cogency.core.agent import Agent

        instructions = f"""
{PROTOSS_CONSTITUTION}

{ARBITER_IDENTITY}

{COORDINATION_PROTOCOL}

{ARBITER_GUIDELINES}
"""

        agent = Agent(instructions=instructions, tools=self.tools)

        response = ""
        async for event in agent(
            context,
            user_id=f"channel-{self.channel_id}",
            conversation_id=f"arbiter-{self.id}",
        ):
            if event["type"] == "respond":
                content = event.get("content", "")
                response += content
                await self.broadcast(event)
            elif event["type"] in ["think", "call", "result"]:
                await self.broadcast(event)

        return response
