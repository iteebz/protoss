"""Core Protoss coordination engine."""

import asyncio
import uuid
import logging
from typing import Optional, List, AsyncIterator, Dict, Any
from dataclasses import dataclass, field

from .config import Config
from . import khala
from .structures import gateway

logger = logging.getLogger(__name__)


@dataclass
class CoordinationEvent:
    """Event emitted during coordination."""
    type: str
    content: str
    agent_id: Optional[str] = None
    pathway_id: Optional[str] = None
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())


class Protoss:
    """Constitutional AI coordination engine.
    
    Usage:
        protoss = Protoss(llm="claude-sonnet", debug=True)
        async for event in protoss("build auth system", agents=5):
            print(event.content)
    """
    
    def __init__(self, **config_kwargs):
        """Initialize coordination engine with configuration.
        
        Args:
            **config_kwargs: Configuration parameters passed to Config
        """
        self.config = Config(**config_kwargs)
        self._initialized = False
        
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.debug("Protoss debug mode enabled")
    
    async def _ensure_initialized(self):
        """Lazy initialization of coordination infrastructure."""
        if not self._initialized:
            logger.info("Initializing Protoss coordination infrastructure")
            
            # Start Khala coordination network
            await khala.start()
            
            self._initialized = True
            logger.info("🔮 Protoss coordination online")
    
    async def __call__(
        self,
        task: str,
        *,
        agents: Optional[int] = None,
        timeout: Optional[int] = None,
        archives: Optional[str] = None,
        pathway_id: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        unit_types: Optional[List[str]] = None
    ) -> AsyncIterator[CoordinationEvent]:
        """Execute coordination task with runtime parameters.
        
        Args:
            task: The coordination task description
            agents: Number of agents (overrides config.agents)
            timeout: Task timeout in seconds (overrides config.timeout)
            archives: Archives directory (overrides config.archives)
            pathway_id: Specific pathway ID (auto-generated if None)
            keywords: Keywords for archon context seeding
            unit_types: Specific unit types to spawn
            
        Yields:
            CoordinationEvent: Real-time coordination updates
        """
        if not task:
            raise ValueError("Task cannot be empty")
        
        await self._ensure_initialized()
        
        # Merge config defaults with runtime overrides
        merged_config = self._merge_runtime_config(
            agents=agents,
            timeout=timeout, 
            archives=archives
        )
        
        # Generate pathway ID if not provided
        pathway_id = pathway_id or f"coord-{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Starting coordination: {task}")
        logger.debug(f"Pathway: {pathway_id}, Agents: {merged_config['agents']}")
        
        # Emit coordination start event
        yield CoordinationEvent(
            type="coordination_start",
            content=f"Coordinating {merged_config['agents']} agents on: {task}",
            pathway_id=pathway_id
        )
        
        try:
            # Execute coordination with timeout
            async with asyncio.timeout(merged_config['timeout']):
                async for event in self._coordinate(
                    task=task,
                    pathway_id=pathway_id,
                    agents=merged_config['agents'],
                    keywords=keywords,
                    unit_types=unit_types
                ):
                    yield event
                    
        except asyncio.TimeoutError:
            yield CoordinationEvent(
                type="coordination_timeout", 
                content=f"Coordination timed out after {merged_config['timeout']} seconds",
                pathway_id=pathway_id
            )
            raise
        except Exception as e:
            yield CoordinationEvent(
                type="coordination_error",
                content=f"Coordination failed: {e}",
                pathway_id=pathway_id
            )
            raise
    
    async def _coordinate(
        self, 
        task: str, 
        pathway_id: str, 
        agents: int,
        keywords: Optional[List[str]] = None,
        unit_types: Optional[List[str]] = None
    ) -> AsyncIterator[CoordinationEvent]:
        """Internal coordination execution."""
        
        # Decide coordination approach based on agents count and context needs
        if keywords or self.config.rich_context:
            # Use archon-seeded coordination for rich context
            yield CoordinationEvent(
                type="context_seeding",
                content="Seeding pathway with archon context",
                pathway_id=pathway_id
            )
            
            result = await gateway.warp_with_context(
                task=task,
                agent_count=agents,
                unit_types=unit_types,
                pathway_id=pathway_id,
                keywords=keywords
            )
        else:
            # Use direct coordination for simple tasks
            result = await gateway.warp(
                task=task,
                agent_count=agents, 
                unit_types=unit_types,
                pathway_id=pathway_id
            )
        
        # Emit coordination completion
        yield CoordinationEvent(
            type="coordination_complete",
            content=result,
            pathway_id=pathway_id
        )
    
    def _merge_runtime_config(
        self, 
        agents: Optional[int] = None,
        timeout: Optional[int] = None,
        archives: Optional[str] = None
    ) -> Dict[str, Any]:
        """Merge configuration defaults with runtime overrides."""
        merged = {
            "agents": agents or self.config.agents,
            "timeout": timeout or self.config.timeout,
            "archives": archives or self.config.archives
        }
        
        # Validate agent count against max_agents
        if merged["agents"] > self.config.max_agents:
            raise ValueError(
                f"Requested {merged['agents']} agents exceeds max_agents={self.config.max_agents}"
            )
        
        return merged
    
    async def status(self) -> Dict[str, Any]:
        """Get coordination system status."""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        khala_status = khala.status()
        pathways = await khala.pathways()
        
        return {
            "status": "online",
            "config": {
                "agents": self.config.agents,
                "max_agents": self.config.max_agents,
                "timeout": self.config.timeout,
                "debug": self.config.debug
            },
            "khala": khala_status,
            "active_pathways": len(pathways),
            "recent_pathways": pathways[:5] if pathways else []
        }
    
    async def shutdown(self):
        """Gracefully shutdown coordination infrastructure."""
        if self._initialized:
            logger.info("Shutting down Protoss coordination")
            await khala.stop()
            self._initialized = False