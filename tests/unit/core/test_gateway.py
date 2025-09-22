"""Gateway spawning function tests."""

import pytest
from protoss.core import gateway


def test_should_spawn_basic():
    """Gateway allows spawning valid agent types."""
    active_agents = {"channel1": set()}

    assert gateway.should_spawn("zealot", "channel1", active_agents)
    assert not gateway.should_spawn("invalid", "channel1", active_agents)


def test_should_spawn_max_agents():
    """Gateway respects max agent limit."""
    active_agents = {"channel1": {"zealot-1", "archon-1"}}

    assert not gateway.should_spawn("oracle", "channel1", active_agents, max_agents=2)
    assert gateway.should_spawn("oracle", "channel1", active_agents, max_agents=5)


def test_should_spawn_duplicate_prevention():
    """Gateway prevents duplicate agent types per channel."""
    active_agents = {"channel1": {"zealot-1"}}

    assert not gateway.should_spawn("zealot", "channel1", active_agents)
    assert gateway.should_spawn("archon", "channel1", active_agents)


@pytest.mark.asyncio
async def test_spawn_agent_invalid_type():
    """Gateway rejects invalid agent types."""
    with pytest.raises(ValueError, match="Unknown agent type"):
        await gateway.spawn_agent("invalid", "channel1", "ws://localhost:8888")
