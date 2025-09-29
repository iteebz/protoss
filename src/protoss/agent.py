"""Constitutional agent with pure conversation coordination."""

import asyncio
import logging
import os
from typing import Optional

try:
    import cogency
except ImportError:
    cogency = None

from .bus import Bus

logger = logging.getLogger(__name__)


class Agent:
    """Agent that coordinates through conversation."""
    
    def __init__(self, agent_type: str, bus: Bus, channel: str = "human", user_id: str = "system"):
        self.agent_type = agent_type
        self.bus = bus
        self.channel = channel
        self.user_id = user_id
        self.conversation_id = channel  # Use channel as conversation_id
        self.running = True
        self.last_poll_time: float = 0  # Track when we last read messages
        
        # Load constitutional identity
        self.identity = self._load_identity()
        
        # Initialize cogency for reasoning
        self.cogency_agent = (
            cogency.Agent(
                llm="gemini",
                instructions=self.identity,
                tools=[],
                history_window=50  # Larger window for coordination context
            ) if cogency else None
        )
        
    def _load_identity(self) -> str:
        """Load constitutional identity from markdown files."""
        # Map agent types to constitution files
        constitution_map = {
            "zealot": "zealot.md",
            "sentinel": "sentinel.md", 
            "harbinger": "harbinger.md"
        }
        
        constitution_file = constitution_map.get(self.agent_type)
        if not constitution_file:
            return f"You are {self.agent_type} - coordinate through conversation."
            
        # Load from constitution folder
        constitution_path = os.path.join(
            os.path.dirname(__file__), 
            "constitution", 
            constitution_file
        )
        
        try:
            with open(constitution_path, 'r') as f:
                base_identity = f.read()
        except FileNotFoundError:
            logger.warning(f"Constitution file not found: {constitution_path}")
            return f"You are {self.agent_type} - coordinate through conversation."
            
        # Add coordination instructions
        coordination_addendum = """

## Coordination Protocol
You coordinate with other agents through pure conversation:
1. Read the conversation history for context
2. Identify what work needs to be done  
3. Claim work conversationally: "I'll handle the database setup"
4. Execute and report progress: "Database schema complete"
5. Coordinate handoffs: "Backend ready, frontend can proceed"
6. Signal completion: "Task complete, !despawn"

Coordinate through dialogue, not tools or special commands."""

        return base_identity + coordination_addendum

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
            return
            
        async for event in self.cogency_agent(
            content, 
            user_id=self.user_id,
            conversation_id=self.conversation_id
        ):
            if event["type"] == "respond":
                response = event["content"]
                await self.bus.send(self.agent_type, response, self.channel)
                
                # Check for despawn signal
                if "!despawn" in response.lower():
                    logger.info(f"Agent {self.agent_type} despawning")
                    self.running = False
                    break