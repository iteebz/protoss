"""The Cathedral Interface: Constitutional coordination as architectural poetry."""

import asyncio
import logging
from typing import Any, Optional
from .config import Config
from .bus import Bus
from .gateway import Gateway
from .server import Server

logger = logging.getLogger(__name__)


class Protoss:
    """Constitutional coordination context manager.
    
    The Cathedral Interface that transforms vision into reality through 
    constitutional dialogue.
    
    Usage:
        async with Protoss("build authentication system") as swarm:
            result = await swarm
    """
    
    def __init__(self, vision: str, config: Optional[Config] = None):
        """Initialize constitutional coordination.
        
        Args:
            vision: The constitutional vision to manifest
            config: Optional configuration (uses defaults if not provided)
        """
        self.vision = vision
        self.config = config or Config()
        self.constitutional_destiny: Optional[Any] = None
        
        # Constitutional infrastructure
        self._bus: Optional[Bus] = None
        self._gateway: Optional[Gateway] = None
        self._server: Optional[Server] = None
        self._channel_id: Optional[str] = None
        
    async def __aenter__(self) -> "Protoss":
        """Constitutional infrastructure genesis."""
        logger.info(f"Initializing constitutional coordination for vision: {self.vision}")
        
        # Initialize Bus coordination network  
        self._bus = Bus()
        await self._bus.start()
        
        # Initialize Gateway spawning facility
        self._gateway = Gateway(self.config)
        
        # Start gateway listening
        await self._gateway.start()
        
        # Create coordination channel and seed constitutional vision
        import uuid
        self._channel_id = f"cathedral_{uuid.uuid4().hex[:8]}"
        await self._seed_constitutional_vision()
        
        logger.info("Constitutional infrastructure active")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Constitutional resource sanctification."""
        logger.info("Sanctifying constitutional resources")
        
        # Clean shutdown of constitutional infrastructure
        if self._gateway:
            await self._gateway.stop()
            
        if self._bus and self._bus.server:
            await self._bus.server.stop()
            
        logger.info("Constitutional coordination complete")
        
    async def __await__(self):
        """Constitutional emergence patience."""
        if not self._channel_id:
            raise RuntimeError("Constitutional coordination not initialized")
            
        # Wait for agents to signal constitutional completion
        return await self._await_constitutional_completion()
        
    async def _seed_constitutional_vision(self):
        """Seed constitutional vision in coordination channel."""
        if not self._channel_id:
            raise RuntimeError("No coordination channel available")
            
        # Send vision message to trigger agent spawning
        # Gateway expects 'vision' type message format
        vision_message = {
            "type": "vision",
            "channel": self._channel_id,
            "content": self.vision
        }
        # Send directly to gateway through bus infrastructure
        if self._bus.server:
            import json
            await self._bus.server.broadcast(json.dumps(vision_message))
        
    async def _await_constitutional_completion(self) -> Any:
        """Monitor coordination dialogue for constitutional signals."""
        completion_signals = ["!complete"]
        
        logger.info("Awaiting constitutional completion...")
        
        while True:
            # Get recent constitutional dialogue
            constitutional_dialogue = self._bus.history(self._channel_id)
            
            if self._constitutional_completion_detected(constitutional_dialogue):
                self.constitutional_destiny = self._extract_constitutional_wisdom(
                    constitutional_dialogue
                )
                logger.info("Constitutional completion detected")
                return self.constitutional_destiny
                
            # Constitutional patience
            await asyncio.sleep(1)
            
    def _constitutional_completion_detected(self, dialogue: list) -> bool:
        """Check if constitutional completion signals are present."""
        completion_signals = ["!complete"]
        
        for message in dialogue[-10:]:  # Check last 10 messages
            if "!complete" in message.content.lower():
                return True
                
        return False
        
    def _extract_constitutional_wisdom(self, dialogue: list) -> str:
        """Extract constitutional wisdom from coordination dialogue."""
        # Find completion message and extract result
        for message in reversed(dialogue):
            content = message.content
            if "!complete" in content.lower():
                # Return the message content as the result
                return content
                
        # Fallback: return summary of recent dialogue
        recent_messages = dialogue[-5:]
        return "\n".join([f"{msg.sender}: {msg.content}" for msg in recent_messages])