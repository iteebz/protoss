"""Zealot: Constitutional AI agent with righteous conviction."""

from .unit import Unit
from ..constitution.identities import ZEALOT_IDENTITY


class Zealot(Unit):
    """Constitutional AI agent - eliminates complexity, enforces principles."""

    @property
    def identity(self) -> str:
        return ZEALOT_IDENTITY

    @property
    def tools(self) -> list:
        from cogency.tools import tools

        return tools.category(["file", "system"])

    async def __call__(self, context: str) -> str:
        """Pure Cogency execution."""
        from cogency.core.agent import Agent

        agent = Agent(
            instructions=f"{self.identity}\n\nCONTEXT:\n{context}", tools=self.tools
        )

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
