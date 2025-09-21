"""Agent lifecycle management for adaptive swarms."""

import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from ..message import Message
from ..agents import Conclave


@dataclass
class AgentState:
    """Track spawned agent state and lifecycle."""

    agent: Any  # Agent instance
    agent_id: str
    agent_type: str
    channel_id: str
    active: bool = True
    conversation_id: Optional[str] = None


class Lifecycle:
    """Manages agent state, but performs no I/O."""

    def __init__(
        self,
        max_agents_per_channel: int = 10,
        factories: Optional[Dict[str, Callable[[str], Any]]] = None,
    ):
        """Initialize agent lifecycle management system.

        Args:
            max_agents_per_channel: Maximum spawned agents per coordination channel
            factories: Optional map of agent factories for dependency injection
        """
        self.max_agents = max_agents_per_channel

        # Channel -> List of AgentState for tracking
        self.agents: Dict[str, List[AgentState]] = {}

        # Agent ID -> AgentState for quick lookup
        self.agent_registry: Dict[str, AgentState] = {}

        # Agent factories (zealot, archon, arbiter, ...)
        self.factories = factories or self._default_factories()

    def _default_factories(self) -> Dict[str, Callable[[str], Any]]:
        """Default agent factories used when none are injected."""
        from ..agents import Zealot, Archon, Arbiter

        return {
            "zealot": Zealot,
            "archon": Archon,
            "arbiter": Arbiter,
        }

    def get_team_status(self, channel_id: str) -> str:
        """Get team composition string for agent awareness."""
        if channel_id not in self.agents:
            return "Team Status: No spawned agents"

        status_parts = []
        for agent_state in self.agents[channel_id]:
            state = "active" if agent_state.active else "inactive"
            status_parts.append(f"{agent_state.agent_id} ({state})")

        if not status_parts:
            return "Team Status: No spawned agents"

        return f"Team Status: {', '.join(status_parts)}"

    def get_active_agents(
        self, channel_id: str, agent_type: Optional[str] = None
    ) -> List[AgentState]:
        """Get list of active agents in channel, optionally filtered by type."""
        if channel_id not in self.agents:
            return []

        agents = [a for a in self.agents[channel_id] if a.active]

        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]

        return agents

    def is_agent_active(self, agent_id: str) -> bool:
        """Check if specific agent is currently active."""
        agent_state = self.agent_registry.get(agent_id)
        return agent_state is not None and agent_state.active

    def can_spawn(self, channel_id: str) -> bool:
        """Check if channel can accept new spawned agents."""
        active_count = len(self.get_active_agents(channel_id))
        return active_count < self.max_agents

    def spawn(
        self, agent_type: str, channel_id: str
    ) -> Optional[str]:
        """Update state to reflect a new agent being spawned. Returns agent_id on success."""
        if not self.can_spawn(channel_id):
            # Logging should be handled by the caller (Gateway)
            return None

        factory = self.factories.get(agent_type)
        if factory is None:
            return None

        agent_id = f"{agent_type}-{uuid.uuid4().hex[:8]}"

        # Note: The agent instance is no longer created here.
        # The AgentState holds metadata, not the live object.
        agent_state = AgentState(
            agent=None, # The live agent object is managed by the Gateway's process
            agent_id=agent_id,
            agent_type=agent_type,
            channel_id=channel_id,
            active=True, # Assumed active on spawn
        )

        if channel_id not in self.agents:
            self.agents[channel_id] = []
        self.agents[channel_id].append(agent_state)
        self.agent_registry[agent_id] = agent_state

        return agent_id


    def respawn(self, agent_id: str) -> Dict[str, any]:
        """Mark an inactive agent as active. Returns a status dictionary."""
        agent_state = self.agent_registry.get(agent_id)

        if agent_state and agent_state.active:
            return {"status": "error", "reason": "already_active"}

        if agent_state and not agent_state.active:
            agent_state.active = True
            return {"status": "success", "action": "respawned"}

        return {"status": "error", "reason": "not_found"}

    def despawn(self, agent_id: str) -> bool:
        """Mark an agent as inactive. Returns True if the agent was found."""
        agent_state = self.agent_registry.get(agent_id)
        if not agent_state:
            return False
        agent_state.active = False
        return True


