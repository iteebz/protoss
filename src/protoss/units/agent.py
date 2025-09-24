"""Single Constitutional AI Agent - Data-driven from registry."""

import logging
import asyncio
from typing import List, Optional, Dict

try:
    import cogency
except ImportError:  # pragma: no cover - optional dependency for live runs
    cogency = None

from ..core.config import Config
from ..core.message import Event
from ..constitution.coordination import PROTOSS_CONSTITUTION, COORDINATION_PROTOCOL
from .unit import Unit

logger = logging.getLogger(__name__)


class Agent(Unit):
    """Pure constitutional AI coordination agent - data-driven from registry."""

    def __init__(
        self,
        unit_type: str,
        channel: str,
        bus_url: str,
        coordination_id: str,
        config: Optional[Config] = None,
    ):
        super().__init__(unit_type, channel, bus_url, coordination_id, config)

        # Initialize cogency for LLM agents
        self.cogency_agent = (
            cogency.Agent(llm="openai", instructions="", tools=self.tools())
            if cogency
            else None
        )

    def tools(self) -> List:
        """Constitutional tools from registry."""
        tool_categories = self.registry_data.get("tools", [])
        try:
            from cogency.tools import tools

            if isinstance(tool_categories, list):
                return tools.category(tool_categories)
            else:
                return tools.category([tool_categories])
        except ImportError:
            logger.warning(
                f"Cogency not available - {self.unit_type} operating with limited capabilities"
            )
            return []

    def _get_identity(self) -> str:
        """Get identity from registry based on agent type and index."""
        identities = self.registry_data["identity"]
        if len(identities) == 1:
            return identities[0]
        else:
            # Multi-identity case (conclave)
            return identities[self.identity_index]

    async def __call__(self, context: str) -> str:
        """Constitutional Cogency execution with registry-driven configuration."""

        identity = self._get_identity()
        guidelines = self.registry_data["guidelines"]

        instructions = f"""
{PROTOSS_CONSTITUTION}

{identity}

{COORDINATION_PROTOCOL}

{guidelines}
"""

        # Update cogency_agent instructions and tools dynamically
        if self.cogency_agent:
            self.cogency_agent.instructions = instructions
            self.cogency_agent.tools = self.tools()
        else:
            logger.warning(f"Cogency agent not initialized for {self.unit_type}")
            return ""

        response = ""
        async for cogency_event in self.cogency_agent(
            context,
            user_id=f"channel-{self.channel}",
            conversation_id=f"{self.unit_type}-{self.unit_id}",
        ):
            if cogency_event["type"] == "respond":
                content = cogency_event.get("content", "")
                response += content
            await self.broadcast(cogency_event)

        return response

    async def broadcast(self, cogency_event: Dict):
        """Broadcast a cogency event to the Bus using the Khala."""
        content = cogency_event.get("content", "")
        await self.send_message(
            content=content,
            event_type="agent_message",
            event_payload=cogency_event,
            coordination_id=self.coordination_id,
        )

    async def execute(self):
        """Execute LLM coordination behavior."""
        while self._running:
            try:
                event = await self.recv_message()
                if event:
                    await self._process_message(event)
            except asyncio.CancelledError:
                logger.info(f"LLM Agent {self.unit_id} cancelled.")
                self._running = False
            except Exception as e:
                logger.error(f"LLM Agent {self.unit_id} error: {e}")

    async def _process_message(self, event: Event):
        """Processes an incoming Event for LLM agents."""
        logger.info(f"LLM Agent {self.unit_id} processing event: {event.type}")

        if event.type == "agent_message" and event.content:
            response = await self(event.content)
            if self._should_despawn(response):
                self._running = False
