"""Conclave: Sacred Four constitutional deliberation through identity injection."""

from .unit import Unit
from ..constitution import (
    PROTOSS_CONSTITUTION,
    COORDINATION_PROTOCOL,
    CONCLAVE_GUIDELINES,
    TASSADAR_IDENTITY,
    ZERATUL_IDENTITY,
    ARTANIS_IDENTITY,
    FENIX_IDENTITY,
)


class Conclave(Unit):
    """Sacred Four constitutional deliberation - identity injected at spawn."""

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        channel_id: str,
        config,
        identity: str = None,
    ):
        super().__init__(agent_id, agent_type, channel_id, config)
        self.sacred_identity = identity

    @property
    def tools(self) -> list:
        from cogency.tools import tools

        return tools.category(["file", "system"])

    def _get_sacred_identity(self) -> str:
        """Map sacred identity string to actual identity constant."""
        sacred_map = {
            "tassadar": TASSADAR_IDENTITY,
            "zeratul": ZERATUL_IDENTITY,
            "artanis": ARTANIS_IDENTITY,
            "fenix": FENIX_IDENTITY,
        }

        if self.sacred_identity not in sacred_map:
            raise ValueError(f"Unknown sacred identity: {self.sacred_identity}")

        return sacred_map[self.sacred_identity]

    async def __call__(self, context: str) -> str:
        """Constitutional Cogency execution with Sacred Four identity injection."""
        from cogency.core.agent import Agent

        identity = self._get_sacred_identity()

        instructions = f"""
{PROTOSS_CONSTITUTION}

{identity}

{COORDINATION_PROTOCOL}

{CONCLAVE_GUIDELINES}
"""

        agent = Agent(instructions=instructions, tools=self.tools)

        response = ""
        async for event in agent(
            context,
            user_id=f"channel-{self.channel_id}",
            conversation_id=f"{self.sacred_identity}-{self.id}",
        ):
            if event["type"] == "respond":
                content = event.get("content", "")
                response += content
                await self.broadcast(event)
            elif event["type"] in ["think", "call", "result"]:
                await self.broadcast(event)

        return response
