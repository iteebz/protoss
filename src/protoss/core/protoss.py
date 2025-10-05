"""Protoss conversational coordination."""

import asyncio
import logging
from .bus import Bus
from .agent import Agent
from ..lib.spawn import build_spawn_context
from ..lib import runs

logger = logging.getLogger(__name__)


class Protoss:
    """Conversational coordination through constitutional agents."""

    def __init__(self, channel: str = "human", base_dir: str = None, run_id: str = None):
        self.bus = Bus(base_dir=base_dir)
        self.agents = []
        self.channel = channel
        self.base_dir = base_dir
        self.run_id = run_id or channel
        self.task = None

    async def start(self):
        """Start the swarm with 3 constitutional agents."""
        # Spawn the 3 constitutional agents
        await self.spawn_agent("zealot")
        await self.spawn_agent("sentinel")
        await self.spawn_agent("harbinger")

        logger.info("Swarm started with 3 constitutional agents")

    async def spawn_agent(
        self, agent_type: str, channel: str = None, parent: str = None
    ):
        """Spawn an agent into the swarm."""
        channel = channel or self.channel
        agent = Agent(
            agent_type, self.bus, channel, base_dir=self.base_dir, protoss=self
        )
        self.agents.append(agent)

        if parent:
            await self.bus.storage.save_message(
                channel=channel,
                sender="system",
                content=f"Channel #{channel} spawned from #{parent}",
                parent=parent,
            )

        # Start agent in background
        asyncio.create_task(agent.run())
        logger.info(f"Spawned {agent_type} in #{channel}")

    async def send_human_message(self, content: str, channel: str = None):
        """Send a message as human with spawn context."""
        if not self.task:
            self.task = content
            
        channel = channel or self.channel
        
        # Check if this is first message in channel
        history = await self.bus.get_history(channel)
        if not history:
            # Inject spawn context for first message
            spawn_context = await build_spawn_context(self.bus.storage, channel)
            content = f"{spawn_context}\n\n{content}"
        
        await self.bus.send("human", content, channel)

    async def wait_for_completion(self, timeout: float = 30.0):
        """Wait for all agents to despawn or timeout."""
        start_time = asyncio.get_event_loop().time()

        while any(agent.running for agent in self.agents):
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.warning("Swarm coordination timeout")
                break
            await asyncio.sleep(0.1)

        logger.info("Swarm coordination complete")

    async def get_conversation(self, channel: str = None):
        """Get full conversation history."""
        channel = channel or self.channel
        return await self.bus.get_history(channel)
    
    async def run(self, task: str, agents: list[str], timeout: float):
        """Execute complete run with telemetry."""
        runs.init()
        runs.start(self.run_id, task, agents, self.channel)
        
        for role in agents:
            await self.spawn_agent(role)
        
        await self.send_human_message(task)
        
        try:
            await self.wait_for_completion(timeout=timeout)
            conv = await self.get_conversation()
            outcome = "timeout" if len(conv) > 0 and any(agent.running for agent in self.agents) else "success"
        except Exception as e:
            outcome = f"error: {e}"
            conv = []
        
        runs.complete(self.run_id, outcome, len(conv))
        return conv
