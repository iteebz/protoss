"""Core Protoss coordination engine."""

import asyncio
import uuid
import logging
from typing import Optional, List, Dict, Any

from .config import Config
from .bus import Bus

logger = logging.getLogger(__name__)


class Protoss:
    """Constitutional AI coordination engine.

    Usage:
        protoss = Protoss(Config(agents=5, debug=True))
        result = await protoss("build auth system")
        print(result)  # "Task completed successfully"
    """

    def __init__(self, config: Config, **overrides):
        """Initialize coordination engine with configuration.

        Args:
            config: Base configuration object
            **overrides: Override specific config fields
        """
        # Clean config override merge
        self.config = config.override(**overrides) if overrides else config
        self.bus = Bus()
        self._initialized = False

        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.debug("Protoss debug mode enabled")

    async def _ensure_initialized(self):
        """Lazy initialization of coordination infrastructure."""
        if not self._initialized:
            logger.info("Initializing Protoss coordination infrastructure")
            await self.bus.start()
            self._initialized = True
            logger.info("🔮 Protoss coordination online")

    async def __call__(
        self,
        task: str,
        *,
        agents: Optional[int] = None,
        timeout: Optional[int] = None,
        channel_id: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> str:
        """Execute coordination task and return result.

        Args:
            task: The coordination task description
            agents: Number of agents (overrides config.agents)
            timeout: Task timeout in seconds (overrides config.timeout)
            channel_id: Specific channel ID (auto-generated if None)
            keywords: Keywords for archon context seeding

        Returns:
            Task completion result
        """
        if not task:
            raise ValueError("Task cannot be empty")

        await self._ensure_initialized()

        # Merge config defaults with runtime overrides
        final_agents = agents or self.config.agents
        final_timeout = timeout or self.config.timeout

        # Validate agent count
        if final_agents > self.config.max_agents:
            raise ValueError(
                f"Requested {final_agents} agents exceeds max_agents={self.config.max_agents}"
            )

        # Generate channel ID if not provided
        channel_id = channel_id or f"coord-{uuid.uuid4().hex[:8]}"

        logger.info(f"Starting coordination: {task}")
        logger.debug(f"Channel: {channel_id}, Agents: {final_agents}")

        try:
            # Execute coordination with timeout
            async with asyncio.timeout(final_timeout):
                return await self._coordinate(
                    task=task,
                    channel_id=channel_id,
                    agents=final_agents,
                    keywords=keywords,
                )

        except asyncio.TimeoutError:
            error_msg = f"Coordination timed out after {final_timeout} seconds"
            logger.error(error_msg)
            raise asyncio.TimeoutError(error_msg)
        except Exception as e:
            logger.error(f"Coordination failed: {e}")
            raise

    async def _coordinate(
        self,
        task: str,
        channel_id: str,
        agents: int,
        keywords: Optional[List[str]] = None,
    ) -> str:
        """Internal coordination execution - adaptive multi-agent orchestration."""
        logger.info(f"Starting adaptive coordination with up to {agents} agents")

        # 1. Rich context seeding if enabled
        archon = None
        if keywords or self.config.rich_context:
            # Import here to avoid circular dependency
            from ..agents import Archon

            archon = Archon()
            context_seed = await archon.seed_channel(task, channel_id, keywords)
            await self.bus.transmit(channel_id, "archon", context_seed)
            logger.debug("Context seeded by archon")

        # 2. Start with minimal coordination team using unified spawning
        initial_agents = min(agents, 2)  # Start minimal - agents summon the rest

        spawned_types: List[str] = []
        for index in range(initial_agents):
            agent_type = "zealot" if index == 0 else "arbiter"
            if await self.bus.spawn(
                agent_type,
                channel_id,
                f"Engine coordination: {task}",
            ):
                spawned_types.append(agent_type)

        logger.debug(f"Spawned initial coordination team: {spawned_types}")

        # Emergent coordination is now handled through the Bus.
        team_status = self.bus.get_team_status(channel_id)

        result_lines = [
            "🔮 PROTOSS COORDINATION ENGAGED",
            f"Task: {task}",
            f"Channel: {channel_id}",
            f"Initial agents: {', '.join(spawned_types) if spawned_types else 'none'}",
            team_status,
            "Emergent coordination active via conversational mentions.",
        ]

        if archon is not None:
            result_lines.append("Archon context seed dispatched.")

        return "\n".join(result_lines)

    async def status(self) -> Dict[str, Any]:
        """Get coordination system status."""
        if not self._initialized:
            return {"status": "not_initialized"}

        bus_status = self.bus.status()
        channels = await self.bus.channels_list()

        return {
            "status": "online",
            "config": {
                "agents": self.config.agents,
                "max_agents": self.config.max_agents,
                "timeout": self.config.timeout,
                "debug": self.config.debug,
            },
            "bus": bus_status,
            "active_channels": len(channels),
            "recent_channels": channels[:5] if channels else [],
        }

    async def shutdown(self):
        """Gracefully shutdown coordination infrastructure."""
        if self._initialized:
            logger.info("Shutting down Protoss coordination")
            await self.bus.stop()
            self._initialized = False
