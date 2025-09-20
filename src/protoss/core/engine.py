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
        """Internal coordination execution - real multi-agent orchestration."""
        from .strategies import get_strategy

        logger.info(f"Starting real coordination with {agents} agents")

        # 1. Rich context seeding if enabled
        archon = None
        if keywords or self.config.rich_context:
            # Import here to avoid circular dependency
            from ..agents import Archon

            archon = Archon()
            context_seed = await archon.seed_channel(task, channel_id, keywords)
            await self.bus.transmit(channel_id, "archon", context_seed)
            logger.debug("Context seeded by archon")

        # 2. Select agents using strategy pattern
        strategy = get_strategy(task, self.config)
        agent_specs = strategy.select_agents(task, agents)

        # Create agent instances from specs using registry
        active_agents = []
        for agent_name, agent_type in agent_specs:
            agent = self._create_agent(agent_type, agent_name)
            active_agents.append((agent_name, agent))

        logger.debug(f"Strategy selected agents: {[name for name, _ in active_agents]}")

        # 3. Coordinate execution through bus
        logger.info(
            f"Spawned {len(active_agents)} agents: {[name for name, _ in active_agents]}"
        )

        # Register all agents to channel
        for _, agent in active_agents:
            self.bus.register(channel_id, agent.id)

        # 4. Execute coordination cycles
        results = []
        for agent_name, agent in active_agents:
            try:
                result = await agent.coordinate(task, channel_id, self.config, self.bus)
                results.append(f"{agent_name}: {result}")
                logger.debug(f"{agent_name} completed coordination")
            except Exception as e:
                logger.error(f"{agent_name} coordination failed: {e}")
                results.append(f"{agent_name}: FAILED - {e}")

        # 5. Synthesize final result
        final_result = self._synthesize_results(task, results)

        # 6. Archive if archon was used
        if archon is not None:
            await archon.compress_channel(channel_id, final_summary=True)

        logger.info("Multi-agent coordination completed")
        return final_result

    def _create_agent(self, agent_type: str, agent_name: str):
        """Create agent instance using clean registry pattern."""

        if agent_type == "Executor":
            from ..agents import Executor

            return Executor()
        elif agent_type == "Zealot":
            from ..agents import Zealot

            return Zealot(agent_name)
        elif agent_type == "Conclave":
            from ..agents import Conclave

            return Conclave("tassadar")
        elif agent_type == "Archon":
            from ..agents import Archon

            return Archon()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    def _synthesize_results(self, task: str, results: List[str]) -> str:
        """Synthesize individual agent results into final coordination outcome."""
        synthesis = [
            "🔮 PROTOSS COORDINATION COMPLETE",
            f"Task: {task}",
            "",
            "Agent Contributions:",
        ]

        for result in results:
            synthesis.append(f"  • {result}")

        synthesis.extend(
            [
                "",
                "Coordination successful - agents achieved collective understanding.",
                "EN TARO ADUN.",
            ]
        )

        return "\n".join(synthesis)

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
