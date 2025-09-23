"""Oracle: External intelligence and web research specialist."""

from .unit import Unit
from ..constitution import (
    PROTOSS_CONSTITUTION,
    ORACLE_IDENTITY,
    COORDINATION_PROTOCOL,
    ORACLE_GUIDELINES,
)


class Oracle(Unit):
    """External intelligence agent - web research and information gathering."""

    @property
    def tools(self) -> list:
        from cogency.tools import tools

        return tools.category("web")

    async def __call__(self, context: str) -> str:
        """Constitutional Cogency execution with external intelligence gathering."""
        from cogency.core.agent import Agent

        instructions = f"""
{PROTOSS_CONSTITUTION}

{ORACLE_IDENTITY}

{COORDINATION_PROTOCOL}

{ORACLE_GUIDELINES}
"""

        agent = Agent(instructions=instructions, tools=self.tools)

        response = ""
        async for event in agent(
            context,
            user_id=f"channel-{self.channel_id}",
            conversation_id=f"oracle-{self.id}",
        ):
            if event["type"] == "respond":
                content = event.get("content", "")
                response += content
                await self.broadcast(event)
            elif event["type"] in ["think", "call", "result"]:
                await self.broadcast(event)

        return response
