"""Constitutional agent with pure conversation coordination."""

import asyncio
import logging
import os
import time
from typing import Optional

try:
    import cogency
except ImportError:
    cogency = None

from .bus import Bus

logger = logging.getLogger(__name__)


class Agent:
    """Agent that coordinates through conversation."""
    
    def __init__(self, agent_type: str, bus: Bus, channel: str = "human", user_id: str = "system", base_dir: str = None):
        self.agent_type = agent_type
        self.bus = bus
        self.channel = channel
        self.user_id = user_id
        self.conversation_id = channel  # Use channel as conversation_id
        self.running = True
        self.last_poll_time: float = 0  # Track when we last read messages
        self.base_dir = base_dir
        
        # Load constitutional identity
        self.identity = self._load_identity()
        
        # Initialize cogency for reasoning with default tools and shared sandbox
        self.cogency_agent = (
            cogency.Agent(
                llm="openai",
                instructions=self.identity,
                base_dir=self.base_dir,  # Shared sandbox for coordination
                # tools=[] - Let cogency provide default tools (web, file, shell)
                history_window=50  # Larger window for coordination context
            ) if cogency else None
        )
        
    def _load_identity(self) -> str:
        """Load constitutional identity from Python modules."""
        try:
            if self.agent_type == "zealot":
                from ..constitution.zealot import IDENTITY
            elif self.agent_type == "sentinel":
                from ..constitution.sentinel import IDENTITY
            elif self.agent_type == "harbinger":
                from ..constitution.harbinger import IDENTITY
            else:
                return f"You are {self.agent_type} - coordinate through conversation."
                
            from ..constitution.coordination import GUIDELINES
            return f"{IDENTITY}\n\n{GUIDELINES}"
            
        except ImportError:
            logger.warning(f"Constitution not found for {self.agent_type}")
            return f"You are {self.agent_type} - coordinate through conversation."

    async def run(self):
        """Main coordination loop - initial context + diff updates."""
        logger.info(f"Agent {self.agent_type} starting in #{self.channel}")
        
        # Initial context assembly - get full channel history
        await self._initial_context_load()
        
        # Coordination loop - process only new messages  
        while self.running:
            try:
                # Get new messages since last poll
                new_messages = self.bus.get_history(
                    channel=self.channel, 
                    since=self.last_poll_time
                )
                
                if new_messages and self.cogency_agent:
                    # Process only the diff - new messages
                    for msg in new_messages:
                        # Skip our own messages
                        if msg['sender'] == self.agent_type:
                            continue
                            
                        # Process new message through cogency
                        await self._process_with_cogency(f"{msg['sender']}: {msg['content']}")
                
                # Update poll timestamp
                self.last_poll_time = time.time()
                
                # Check if we should continue
                if not self.running:
                    break
                    
                # Coordination heartbeat - pause before next cycle
                await asyncio.sleep(2.0)
                
            except Exception as e:
                logger.error(f"Agent {self.agent_type} coordination error: {e}")
                break
                
        logger.info(f"Agent {self.agent_type} stopping")
        
    async def _initial_context_load(self):
        """Load full channel history on agent spawn."""
        history = self.bus.get_history(self.channel)
        
        if history and self.cogency_agent:
            # Format full conversation for initial context
            context = self._format_history(history)
            logger.info(f"Agent {self.agent_type} loading initial context: {len(history)} messages")
            
            # Process full history as initial context
            await self._process_with_cogency(f"Channel history:\n{context}")
            
        # Set poll time to now - future polls will only get diffs  
        self.last_poll_time = time.time()
    
    def _format_history(self, history) -> str:
        """Format message history for context."""
        return "\n".join([
            f"{msg['sender']}: {msg['content']}" 
            for msg in history
        ])
        
    async def _process_with_cogency(self, content: str):
        """Process content through cogency and respond."""
        if not self.cogency_agent:
            logger.warning(f"Agent {self.agent_type} has no cogency agent")
            return
            
        async for event in self.cogency_agent(
            content, 
            user_id=self.user_id,
            conversation_id=self.conversation_id
        ):            
            if event["type"] == "respond":
                response = event["content"]
                logger.info(f"{self.agent_type}: {response}\n")
                await self.bus.send(self.agent_type, response, self.channel)
                
                # Check for exit signals
                if "!despawn" in response.lower():
                    logger.info(f"Agent {self.agent_type} despawning")
                    self.running = False
                    break
                    
                if "!complete" in response.lower():
                    logger.info(f"Agent {self.agent_type} signaling task complete")
                    # Don't despawn on !complete - let other agents see it and decide
                    
            elif event["type"] == "end":
                # §end breaks the reasoning cycle - return to diff polling
                break