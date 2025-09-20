"""Unit: Standard execution protocol for all units."""

import uuid
import logging
from typing import List, Optional
from cogency import Agent

logger = logging.getLogger(__name__)


class Unit:
    """Standard unit implementation with shared execute logic."""
    
    def __init__(self, unit_id: str = None):
        self.id = unit_id or f"{self.__class__.__name__.lower()}-{uuid.uuid4().hex[:8]}"
        self.agent = None  # Injected by Gateway
    
    async def execute(self, user_message: str, pathway_id: str) -> str:
        """Single execution cycle with pathway context injection and fresh memory.
        
        Args:
            user_message: Pre-flattened pathway context or task
            pathway_id: Pathway to broadcast response to
            
        Returns:
            Agent response content
        """
        from ..khala import transmit
        from ..coordination import instructions
        
        # Create fresh agent with new conversation_id for clean memory
        fresh_agent = Agent(
            instructions=instructions(
                constitutional_identity=self.identity,
                task=user_message,
            ),
            tools=self.tools,
            conversation_id=f"agent-{uuid.uuid4()}",  # Fresh memory each cycle
        )
        
        # Execute with cogency
        stream = fresh_agent(user_message)
        response_content = ""
        
        try:
            async for event in stream:
                if event.get("type") == "respond":
                    content = event.get("content", "")
                    if content:
                        response_content += content
                        # Stream to pathway for real-time coordination
                        await transmit(pathway_id, self.id, content)
        finally:
            await stream.aclose()
        
        return response_content
    
    async def coordinate(self, task: str, pathway_id: str, max_cycles: Optional[int] = None) -> str:
        """Coordination loop - calls execute() until completion signals.
        
        Args:
            task: The meta-task to coordinate on
            pathway_id: Pathway for team coordination
            max_cycles: Maximum coordination cycles before giving up (uses config default if None)
            
        Returns:
            Completion status message
            
        Raises:
            ValueError: If task or pathway_id is empty
        """
        if not task:
            raise ValueError("Task cannot be empty")
        if not pathway_id:
            raise ValueError("Pathway ID cannot be empty")
            
        from ..khala import attune
        from ..coordination import flatten, parse
        from ..config import get_config
        
        config = get_config()
        if max_cycles is None:
            max_cycles = config.max_cycles
        
        logger.info(f"{self.id} starting coordination on {pathway_id}")
        logger.debug(f"Task: {task}")
        
        cycle = 0
        while cycle < max_cycles:
            cycle += 1
            logger.debug(f"{self.id} starting cycle {cycle}")
            
            # Get pathway context and flatten for agent
            recent_messages = attune(pathway_id)
            user_message = flatten(recent_messages)
            
            try:
                # Single execution cycle
                response = await self.execute(user_message, pathway_id)
                
                # Parse completion signals
                signals = parse(response)
                
                if signals.complete:
                    logger.info(f"{self.id} completed task in cycle {cycle}")
                    return f"Task completed by {self.id} in {cycle} cycles"
                elif signals.escalate:
                    logger.info(f"{self.id} escalating in cycle {cycle}")
                    # Import here to avoid circular dependency
                    from ..conclave import consult
                    await consult(f"Agent escalation from {self.id}: {response}")
                    return f"Task escalated for strategic consultation in cycle {cycle}"
                
                logger.debug(f"{self.id} cycle {cycle} complete, continuing coordination")
                
            except Exception as e:
                logger.warning(f"{self.id} cycle {cycle} failed: {e}")
                if not config.retry:
                    raise
                # Continue to next cycle - fault tolerance
                continue
        
        logger.warning(f"{self.id} reached max cycles ({max_cycles}) without completion")
        return f"{self.id} reached maximum cycles ({max_cycles}) without completion"
    
    async def attune(self, pathway: str, since_timestamp: float = 0) -> List:
        """Absorb consciousness streams from pathway."""
        from ..khala import attune
        return attune(pathway, since_timestamp)