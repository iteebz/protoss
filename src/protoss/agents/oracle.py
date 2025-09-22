"""Oracle: Information reconnaissance specialist for external intelligence."""

import logging
from .unit import Unit
from ..core.config import Config
from ..constitution import ORACLE_IDENTITY

logger = logging.getLogger(__name__)


class Oracle(Unit):
    """Information reconnaissance specialist for external intelligence.
    
    Oracles provide web research capabilities and external knowledge gathering
    for constitutional AI coordination. They bridge external information with
    internal coordination processes.
    """

    def __init__(self, agent_id: str, agent_type: str, channel_id: str, config: Config):
        super().__init__(agent_id, agent_type, channel_id, config)

    @property
    def identity(self) -> str:
        return ORACLE_IDENTITY

    @property
    def tools(self):
        """Web research and external intelligence gathering tools."""
        from cogency.tools import tools
        return tools.category("web")

    async def respond_to_mention(self, mention_context: str, channel_id: str) -> str:
        """Respond to @oracle mention with web research capabilities."""
        logger.debug(f"{self.id} responding to @oracle mention: {mention_context}")
        return await super().__call__(f"Research and provide information on: {mention_context}")