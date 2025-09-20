"""Integration tests for unified spawning architecture (mocked)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from protoss.core.bus import Bus
from protoss.core.engine import Protoss
from protoss.core.config import Config


@pytest.fixture
def mock_agent():
    """Create mock agent that doesn't call LLMs."""
    agent = MagicMock()
    agent.id = "test-agent-123"
    agent.coordinate = AsyncMock(return_value="Mock coordination complete")
    return agent


@pytest.fixture
def bus():
    """Create Bus instance for testing."""
    import random

    port = random.randint(9000, 9999)  # Use random port to avoid conflicts
    return Bus(port=port, enable_storage=False)


@pytest.mark.asyncio
async def test_bus_spawn_fresh_agent(bus, mock_agent):
    """Test bus.spawn() creates fresh agent."""

    def zealot_factory(agent_id: str):
        mock_agent.id = agent_id
        return mock_agent

    with patch.dict(bus.spawner.factories, {"zealot": zealot_factory}):
        result = await bus.spawn("zealot", "squad-test", "Test spawn")

    assert result is True

    active_agents = bus.spawner.get_active_agents("squad-test", "zealot")
    assert len(active_agents) == 1
    assert active_agents[0].agent_type == "zealot"


@pytest.mark.asyncio
async def test_bus_spawn_reactivate_agent(bus, mock_agent):
    """Test bus.spawn() can reactivate despawned agent."""

    def zealot_factory(agent_id: str):
        mock_agent.id = agent_id
        return mock_agent

    with patch.dict(bus.spawner.factories, {"zealot": zealot_factory}):
        await bus.spawn("zealot", "squad-reactivate", "Test spawn")

    active_agents = bus.spawner.get_active_agents("squad-reactivate", "zealot")
    agent_id = active_agents[0].agent_id

    await bus.despawn(agent_id)
    assert not bus.spawner.is_agent_active(agent_id)

    await bus.spawn(agent_id, "squad-reactivate", "Reactivate")
    assert bus.spawner.is_agent_active(agent_id)


@pytest.mark.asyncio
async def test_engine_uses_unified_spawning():
    """Test engine uses bus.spawn() instead of direct agent creation."""

    config = Config(agents=2, timeout=10, debug=True)
    engine = Protoss(config)

    # Mock bus.spawn to track calls
    with (
        patch.object(engine.bus, "start", new=AsyncMock()),
        patch.object(engine.bus, "stop", new=AsyncMock()),
        patch.object(engine.bus, "spawn", new_callable=AsyncMock) as mock_spawn,
    ):
        mock_spawn.return_value = True

        result = await engine("Test task")

        # Verify spawn was called for initial agents
        assert mock_spawn.call_count >= 1

        agent_types = [call.args[0] for call in mock_spawn.call_args_list]
        assert "zealot" in agent_types or "arbiter" in agent_types

        assert "PROTOSS COORDINATION ENGAGED" in result

        await engine.shutdown()


@pytest.mark.asyncio
async def test_no_dual_agent_creation_paths():
    """Verify engine doesn't use _create_agent anymore."""

    config = Config(agents=1, timeout=5)
    engine = Protoss(config)

    # Verify _create_agent method doesn't exist
    assert not hasattr(engine, "_create_agent")

    await engine.shutdown()


@pytest.mark.asyncio
async def test_spawner_handles_both_patterns(bus, mock_agent):
    """Test spawner handles both type and specific ID patterns."""

    def zealot_factory(agent_id: str):
        mock_agent.id = agent_id
        return mock_agent

    with patch.dict(bus.spawner.factories, {"zealot": zealot_factory}):
        await bus.spawn("zealot", "squad-pattern", "Type spawn")

    active_agents = bus.spawner.get_active_agents("squad-pattern", "zealot")
    assert len(active_agents) == 1

    agent_id = active_agents[0].agent_id

    await bus.despawn(agent_id)
    await bus.spawn(agent_id, "squad-pattern", "ID reactivation")

    assert bus.spawner.is_agent_active(agent_id)
