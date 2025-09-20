"""Agent spawning and lifecycle management for adaptive swarms."""

import uuid
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from .message import Message


@dataclass
class AgentState:
    """Track spawned agent state and lifecycle."""

    agent: Any  # Agent instance
    agent_id: str
    agent_type: str
    channel_id: str
    active: bool = True
    conversation_id: Optional[str] = None


class Spawner:
    """Manages agent spawning, awakening, and lifecycle for adaptive coordination."""

    def __init__(
        self,
        max_agents_per_channel: int = 10,
        factories: Optional[Dict[str, Callable[[str], Any]]] = None,
    ):
        """Initialize spawn management system.

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

    async def handle_mention(self, message: Message, bus) -> bool:
        """Handle @ mentions for spawning/awakening. Returns True if handled."""
        mentions = self._extract_mentions(message.content)

        for mention in mentions:
            if mention == "human":
                # Special case - bubble to engine
                await self._handle_human_escalation(message, bus)
                return True

            if self._is_specific_agent_mention(mention):
                # Existing agent respawn
                await self._respawn(mention, message.channel, message, bus)

                base = mention.split("-", 1)[0]
                agent_type = self._resolve_agent_type(base)

                if agent_type in {"archon", "arbiter", "conclave"}:
                    await self._dispatch_responses(
                        agent_type,
                        message,
                        bus,
                        target_agent_id=mention,
                    )

                continue

            base_mention = mention.split("-", 1)[0]

            if base_mention in ["zealot", "archon", "arbiter", "conclave"]:
                if base_mention == "archon":
                    active_archons = self.get_active_agents(
                        message.channel, "archon"
                    )
                    if not active_archons:
                        await self._spawn(base_mention, message.channel, message, bus)
                    await self._dispatch_responses("archon", message, bus)
                elif base_mention == "arbiter":
                    active_arbiters = self.get_active_agents(
                        message.channel, "arbiter"
                    )
                    if not active_arbiters:
                        await self._spawn(base_mention, message.channel, message, bus)
                    await self._dispatch_responses("arbiter", message, bus)
                else:
                    # Fresh agent spawn for non-archon mentions
                    await self._spawn(base_mention, message.channel, message, bus)

                    if base_mention == "conclave":
                        await self._dispatch_responses("conclave", message, bus)

            else:
                await bus.transmit(
                    message.channel,
                    "system",
                    f"❓ Unknown agent type '{mention}'",
                )

        return len(mentions) > 0

    async def _dispatch_responses(
        self,
        agent_type: str,
        message: Message,
        bus,
        target_agent_id: Optional[str] = None,
    ) -> None:
        """Have active agents respond to a mention."""

        agents = self.get_active_agents(message.channel, agent_type)

        if target_agent_id:
            agents = [a for a in agents if a.agent_id == target_agent_id]

        if not agents:
            return

        # Prefer deterministic selection
        for agent_state in agents:
            agent_impl = getattr(agent_state, "agent", None)
            if not agent_impl or not hasattr(agent_impl, "respond_to_mention"):
                continue

            try:
                response = await agent_impl.respond_to_mention(
                    message.content, message.channel
                )
            except Exception as exc:  # pragma: no cover - defensive
                await bus.transmit(
                    message.channel,
                    "system",
                    f"⚠️ {agent_state.agent_id} failed to respond: {exc}",
                )
                continue

            if not response:
                continue

            await bus.transmit(message.channel, agent_state.agent_id, response)

    async def despawn_agent(self, agent_id: str) -> bool:
        """Handle agent !despawn command. Returns True if despawned."""
        agent_state = self.agent_registry.get(agent_id)
        if not agent_state:
            return False

        # Mark as inactive but keep in registry for potential resurrection
        agent_state.active = False

        # Remove from active channel tracking
        if agent_state.channel_id in self.agents:
            # Keep in list but marked inactive for team status visibility
            pass

        return True

    def _extract_mentions(self, content: str) -> List[str]:
        """Extract @mentions from message content."""
        return re.findall(r"@(\w+(?:-\w+)*)", content)

    def _is_specific_agent_mention(self, mention: str) -> bool:
        """Check if mention targets specific agent (e.g., zealot-abc123)."""
        return "-" in mention and any(
            mention.startswith(agent_type + "-")
            for agent_type in [
                "zealot",
                "archon",
                "conclave",
                "arbiter",
                "tassadar",
                "zeratul",
                "artanis",
                "fenix",
            ]
        )

    def _resolve_agent_type(self, base: str) -> str:
        """Map mention prefix to canonical agent type."""
        if base in {"tassadar", "zeratul", "artanis", "fenix"}:
            return "conclave"
        return base

    async def _spawn(
        self, agent_type: str, channel_id: str, trigger_message: Message, bus
    ) -> bool:
        """Spawn new agent of specified type. Returns True on success."""

        # Special case: conclave summons constitutional perspectives together
        if agent_type == "conclave":
            return await self._summon_conclave(channel_id, trigger_message, bus)

        # Check if agent type already active (idempotent spawning)
        existing_agents = self.get_active_agents(channel_id, agent_type)
        if existing_agents:
            await bus.transmit(
                channel_id,
                "system",
                f"✋ {existing_agents[0].agent_id} already active - use natural addressing",
            )
            return False

        # Respect max agent cap per channel
        if not self.can_spawn(channel_id):
            await bus.transmit(
                channel_id,
                "system",
                f"🚫 Max agents ({self.max_agents}) reached in channel",
            )
            return False

        # Locate factory for requested agent type
        factory = self.factories.get(agent_type)
        if factory is None:
            await bus.transmit(
                channel_id,
                "system",
                f"❓ Unknown agent type '{agent_type}'",
            )
            return False

        agent_id = f"{agent_type}-{uuid.uuid4().hex[:8]}"

        try:
            agent = factory(agent_id)
        except Exception as exc:  # pragma: no cover - defensive guard
            await bus.transmit(
                channel_id,
                "system",
                f"❌ Failed to spawn {agent_type}: {exc}",
            )
            return False

        # Register agent state
        agent_state = AgentState(
            agent=agent,
            agent_id=agent_id,
            agent_type=agent_type,
            channel_id=channel_id,
            active=True,
        )

        if channel_id not in self.agents:
            self.agents[channel_id] = []
        self.agents[channel_id].append(agent_state)
        self.agent_registry[agent_id] = agent_state

        # Register to bus and announce presence
        bus.register(channel_id, agent_id)

        await bus.transmit(
            channel_id,
            "system",
            f"🔮 Spawned {agent_id} for {agent_type} expertise",
        )

        return True

    async def _summon_conclave(
        self, channel_id: str, trigger_message: Message, bus
    ) -> bool:
        """Summon all four Conclave perspectives for strategic consultation."""

        # Ensure capacity for the Sacred Four
        if len(self.get_active_agents(channel_id)) + 4 > self.max_agents:
            await bus.transmit(
                channel_id,
                "system",
                f"🚫 Cannot spawn conclave - would exceed max agents ({self.max_agents})",
            )
            return False

        from ..agents import Conclave

        spawned_count = 0
        errors: List[str] = []

        for perspective in ["tassadar", "zeratul", "artanis", "fenix"]:
            agent_id = f"{perspective}-{uuid.uuid4().hex[:8]}"

            try:
                agent = Conclave(perspective, agent_id)
            except Exception as exc:  # pragma: no cover - defensive guard
                errors.append(f"{perspective}: {exc}")
                continue

            agent_state = AgentState(
                agent=agent,
                agent_id=agent_id,
                agent_type="conclave",
                channel_id=channel_id,
                active=True,
            )

            if channel_id not in self.agents:
                self.agents[channel_id] = []
            self.agents[channel_id].append(agent_state)
            self.agent_registry[agent_id] = agent_state

            bus.register(channel_id, agent_id)
            spawned_count += 1

        if spawned_count:
            await bus.transmit(
                channel_id,
                "system",
                f"🏛️ Conclave assembled: {spawned_count} members forming independent positions",
            )
            if errors:
                await bus.transmit(
                    channel_id,
                    "system",
                    f"⚠️ {len(errors)} conclave members failed to spawn: {'; '.join(errors)}",
                )
            return True

        await bus.transmit(
            channel_id,
            "system",
            f"❌ Failed to spawn any conclave members: {'; '.join(errors)}",
        )
        return False

    async def _respawn(
        self, agent_id: str, channel_id: str, trigger_message: Message, bus
    ) -> bool:
        """Awaken or resurrect specific agent. Returns True on success."""
        agent_state = self.agent_registry.get(agent_id)

        if agent_state and agent_state.active:
            await bus.transmit(
                channel_id,
                "system",
                f"✨ {agent_id} already active and participating",
            )
            return False

        if agent_state and not agent_state.active:
            agent_state.active = True
            await bus.transmit(
                channel_id,
                "system",
                f"🔄 Reactivated {agent_id} with previous context",
            )
            bus.register(channel_id, agent_id)
            return True

        await bus.transmit(
            channel_id,
            "system",
            f"❓ Agent {agent_id} not found - use @{agent_id.split('-')[0]} to spawn fresh",
        )
        return False

    async def _handle_human_escalation(self, message: Message, bus):
        """Handle @human escalation - should bubble to engine."""
        await bus.transmit(
            message.channel,
            "system",
            f"🚨 Human escalation: {message.content}",
        )
        # TODO: Implement actual escalation bubbling to engine
