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

    def __init__(self, config: Optional[Config] = None, bus: Bus = None, **overrides):
        """Initialize coordination engine with configuration.

        Args:
            config: Base configuration object (defaults to loading from env)
            bus: Optional Bus instance for dependency injection
            **overrides: Override specific config fields
        """
        # Load config from environment if not provided, then apply overrides
        base_config = config or Config.from_env()
        self.config = base_config.override(**overrides)
        self.bus = bus or Bus()
        self._initialized = False

        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.debug("Protoss debug mode enabled")

    async def _ensure_initialized(self):
        """Lazy initialization of coordination infrastructure."""
        if not self._initialized:
            logger.info("Initializing Protoss coordination infrastructure")
            if not self.bus.is_running(): # Check if bus is already running
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
        """Internal coordination execution: seed context and request initial agents."""
        logger.info(f"Requesting coordination for up to {agents} agents")

        # The Protoss engine transmits the task to the channel for agents to consume.
        await self.bus.transmit(channel_id, "protoss_engine", f"TASK: {task}")

        # 1. Rich context seeding if enabled
        if keywords or self.config.rich_context:
            spawn_request = {
                "type": "spawn_req",
                "channel": channel_id,
                "content": {
                    "agent_type": "archon",
                    "task": f"Seed channel context for: {task}",
                    "keywords": keywords,
                },
            }
            await self.bus.transmit("gateway_commands", "protoss_engine", json.dumps(spawn_request))
            logger.debug("Context seeding requested via Archon")

        # 2. Request initial agents by sending spawn requests to the dedicated gateway_commands channel
        initial_agents = min(agents, 2)
        spawned_types: List[str] = []
        for index in range(initial_agents):
            agent_type = "zealot" if index == 0 else "arbiter"
            spawn_request = {
                "type": "spawn_req",
                "channel": channel_id,
                "content": {
                    "agent_type": agent_type,
                    "task": f"Engine coordination: {task}",
                },
            }
            # The Gateway listens for this message type on the gateway_commands channel
            await self.bus.transmit("gateway_commands", "protoss_engine", json.dumps(spawn_request))
            spawned_types.append(agent_type)

        logger.debug(f"Requested initial coordination team: {spawned_types}")

        # The engine's responsibility ends here. The Gateway and Agents are autonomous.
        result_lines = [
            "🔮 PROTOSS COORDINATION ENGAGED",
            f"Task: {task}",
            f"Channel: {channel_id}",
            f"Initial agent types requested: {', '.join(spawned_types) if spawned_types else 'none'}",
            "Engine has requested the swarm. The Gateway is now responsible for spawning.",
            "Monitor the bus for emergent coordination.",
        ]

        return "\n".join(result_lines)


    async def status(self) -> Dict[str, Any]:
        """Get coordination system status."""
        if not self._initialized:
            return {"status": "not_initialized"}

        # The Bus no longer exposes direct status or channel lists.
        # This information would need to be gathered via message passing.
        return {
            "status": "online",
            "config": {
                "agents": self.config.agents,
                "max_agents": self.config.max_agents,
                "timeout": self.config.timeout,
                "debug": self.config.debug,
            },
            "bus": "Status to be gathered via message passing",
            "active_channels": "To be gathered via message passing",
            "recent_channels": "To be gathered via message passing",
        }

    async def shutdown(self):
        """Gracefully shutdown coordination infrastructure."""
        if self._initialized:
            logger.info("Shutting down Protoss coordination")
            await self.bus.stop()
            self._initialized = False
