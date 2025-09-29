"""Protoss conversational coordination."""

import asyncio
import logging
from .bus import Bus
from .agent import Agent

logger = logging.getLogger(__name__)


class Protoss:
    """Conversational coordination through constitutional agents."""
    
    def __init__(self, channel: str = "human", base_dir: str = None):
        self.bus = Bus()
        self.agents = []
        self.channel = channel
        self.base_dir = base_dir
        
    async def start(self):
        """Start the swarm with 3 constitutional agents."""
        # Spawn the 3 constitutional agents
        await self.spawn_agent("zealot")
        await self.spawn_agent("sentinel") 
        await self.spawn_agent("harbinger")
        
        logger.info("Swarm started with 3 constitutional agents")
        
    async def spawn_agent(self, agent_type: str, channel: str = None):
        """Spawn an agent into the swarm."""
        channel = channel or self.channel
        agent = Agent(agent_type, self.bus, channel, base_dir=self.base_dir)
        self.agents.append(agent)
        
        # Start agent in background
        asyncio.create_task(agent.run())
        logger.info(f"Spawned {agent_type} in #{channel}")
        
    async def send_human_message(self, content: str, channel: str = None):
        """Send a message as human."""
        channel = channel or self.channel
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
        
    def get_conversation(self, channel: str = None):
        """Get full conversation history."""
        channel = channel or self.channel
        return self.bus.get_history(channel)