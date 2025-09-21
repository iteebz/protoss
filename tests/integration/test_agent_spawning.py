"""Integration tests for agent spawning and lifecycle management."""

import pytest
from protoss.core.bus import Bus
from protoss.core.config import Config
from protoss.agents import Zealot


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mention_spawning(monkeypatch):
    """Test @mention spawning and team awareness."""

    # Mock cogency agent for predictable spawning test
    class SpawningMockAgent:
        def __init__(self, instructions=None, tools=None, **kwargs):
            self.instructions = instructions
            self.tools = tools or []

        async def __call__(
            self, user_message, user_id=None, conversation_id=None, chunks=False
        ):
            # Always mention @zealot for predictable test
            if "ZEALOT" in (self.instructions or ""):
                yield {
                    "type": "respond",
                    "content": "I need architectural review. @zealot assistance needed.",
                }
            else:
                # Spawned agents respond normally
                yield {
                    "type": "respond",
                    "content": "Architectural review complete. !despawn",
                }
            yield {"type": "end"}

    monkeypatch.setattr("cogency.core.agent.Agent", SpawningMockAgent)

    # Setup bus with spawner
    bus = Bus(enable_storage=False)
    config = Config(debug=True, max_cycles=2)

    # Create initial zealot
    zealot = Zealot("zealot-original")

    # Coordinate - should trigger @zealot mention and spawning
    await zealot.coordinate(
        "Design authentication system", "squad-spawning", config, bus
    )

    # Verify spawning occurred
    team_status = bus.get_team_status("squad-spawning")
    assert "zealot-" in team_status, "Should show spawned zealot in team status"

    # Verify messages show spawning
    messages = bus.memories["squad-spawning"]
    spawn_messages = [msg for msg in messages if "Spawned" in msg.content]
    assert len(spawn_messages) > 0, "Should have spawning notification"

    # Verify @mention detected
    mention_messages = [msg for msg in messages if "@zealot" in msg.content]
    assert len(mention_messages) > 0, "Should have @zealot mention"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_despawn_lifecycle(monkeypatch):
    """Test !despawn lifecycle management."""

    # Mock agent that signals !despawn
    class DespawnMockAgent:
        def __init__(self, instructions=None, tools=None, **kwargs):
            self.instructions = instructions
            self.tools = tools or []

        async def __call__(
            self, user_message, user_id=None, conversation_id=None, chunks=False
        ):
            yield {"type": "respond", "content": "Work complete. !despawn"}
            yield {"type": "end"}

    monkeypatch.setattr("cogency.core.agent.Agent", DespawnMockAgent)

    bus = Bus(enable_storage=False)
    config = Config(debug=True, max_cycles=1)
    zealot = Zealot("zealot-lifecycle")

    # Coordinate - should trigger !despawn
    result = await zealot.coordinate("Simple task", "squad-lifecycle", config, bus)

    # Verify despawn occurred
    assert "despawned successfully" in result, "Should indicate successful despawn"

    # Verify spawner tracked the despawn
    spawner = bus.spawner
    agent_state = spawner.agent_registry.get("zealot-lifecycle")
    if agent_state:  # May be None if not tracked by spawner
        assert not agent_state.active, "Agent should be marked inactive"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_spawner_max_agents_limit():
    """Test spawner respects max agents per channel."""

    bus = Bus(enable_storage=False)
    channel_id = "test-channel"

    # Set low limit for testing
    bus.spawner.max_agents = 2

    # Try to spawn agents beyond limit
    from protoss.core.message import Message

    trigger_msg = Message(channel_id, "test", "Need help")

    # Should succeed
    assert await bus.spawner._spawn("zealot", channel_id, trigger_msg, bus)
    assert await bus.spawner._spawn("archon", channel_id, trigger_msg, bus)

    # Should fail (max reached)
    assert not await bus.spawner._spawn("conclave", channel_id, trigger_msg, bus)

    # Verify only 2 agents spawned
    team_status = bus.get_team_status(channel_id)
    agent_count = len([line for line in team_status.split() if "active" in line])
    assert agent_count == 2, "Should respect max agents limit"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_reactivation():
    """Test @agent-id reactivation of despawned agents."""

    bus = Bus(enable_storage=False)
    spawner = bus.spawner

    # Manually create despawned agent state
    from protoss.core.spawner import AgentState
    from protoss.agents import Zealot

    agent = Zealot("zealot-123")
    channel_id = "squad-reactivation"
    agent_state = AgentState(agent, "zealot-123", "zealot", channel_id, active=False)

    spawner.agent_registry["zealot-123"] = agent_state
    spawner.agents[channel_id] = [agent_state]

    # Create message mentioning specific agent
    from protoss.core.message import Message

    trigger_msg = Message(channel_id, "test", "Need @zealot-123 help")

    # Should reactivate
    success = await spawner._respawn("zealot-123", channel_id, trigger_msg, bus)
    assert success

    # Verify reactivation
    assert agent_state.active, "Agent should be reactivated"

    # Verify message sent
    if channel_id in bus.memories:
        messages = bus.memories[channel_id]
        reactivation_messages = [
            msg for msg in messages if "Reactivated" in msg.content
        ]
        assert len(reactivation_messages) > 0, "Should have reactivation notification"
