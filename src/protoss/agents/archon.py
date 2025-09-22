"""Archon: Constitutional memory keeper with archive scope."""

from .unit import Unit
from ..constitution.identities import ARCHON_IDENTITY


class Archon(Unit):
    """Constitutional archive agent - restricted to archives/ directory."""

    @property
    def identity(self) -> str:
        return ARCHON_IDENTITY

    @property
    def tools(self) -> list:
        from cogency.tools import tools

        return tools.category("file")

    async def __call__(self, context: str) -> str:
        """Pure Cogency execution with archive scope."""
        from cogency.core.agent import Agent

        agent = Agent(
            instructions=f"{self.identity}\n\nCONTEXT:\n{context}", tools=self.tools
        )

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
