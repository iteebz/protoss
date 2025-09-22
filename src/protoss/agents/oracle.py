"""Oracle: External intelligence and web research specialist."""

from .unit import Unit
from ..constitution.identities import ORACLE_IDENTITY


class Oracle(Unit):
    """External intelligence agent - web research and information gathering."""

    @property
    def identity(self) -> str:
        return ORACLE_IDENTITY

    @property
    def tools(self) -> list:
        from cogency.tools import tools

        return tools.category("web")

    async def __call__(self, context: str) -> str:
        """Pure Cogency execution with web research capabilities."""
        from cogency.core.agent import Agent

        agent = Agent(
            instructions=f"{self.identity}\n\nCONTEXT:\n{context}", tools=self.tools
        )

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
