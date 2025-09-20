"""Integration tests for adaptive agent summoning."""

import pytest
from protoss.core.bus import Bus
from protoss.agents import Zealot


@pytest.mark.integration
@pytest.mark.asyncio
async def test_zealot_summoning(mock_agent):
    """Test @zealot mention spawns new zealot agent."""
    bus = Bus(max_agents=5, enable_storage=False)

    zealot = Zealot("zealot-initial")
    channel_id = "squad-summoning"
    bus.register(channel_id, zealot.id)

    await bus.transmit(
        channel_id,
        zealot.id,
        "Need architectural review. @zealot assistance requested.",
    )

    spawned_agents = bus.spawner.get_active_agents(channel_id, "zealot")
    assert len(spawned_agents) == 1

    channel_agents = bus.channels[channel_id]
    assert len(channel_agents) == 2  # original + spawned
    assert spawned_agents[0].agent_id in channel_agents

    messages = bus.history(channel_id)
    spawn_messages = [msg for msg in messages if "Spawned" in msg.content]
    assert len(spawn_messages) == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_agent_types_summoning(mock_agent):
    """Test summoning different agent types."""
    bus = Bus(max_agents=10, enable_storage=False)

    channel_id = "squad-multi-spawn"

    await bus.transmit(
        channel_id, "system", "Need @zealot for review and @archon for context"
    )
    await bus.transmit(channel_id, "system", "Also need @conclave for deliberation")

    zealots = bus.spawner.get_active_agents(channel_id, "zealot")
    archons = bus.spawner.get_active_agents(channel_id, "archon")
    conclave = bus.spawner.get_active_agents(channel_id, "conclave")

    assert len(zealots) == 1
    assert len(archons) == 1
    assert len(conclave) == 4  # Sacred Four perspectives


@pytest.mark.integration
@pytest.mark.asyncio
async def test_max_agents_enforcement(mock_agent):
    """Test max_agents limit prevents unlimited spawning."""
    bus = Bus(max_agents=2, enable_storage=False)

    channel_id = "squad-limited"

    await bus.transmit(channel_id, "system", "@zealot help needed")
    await bus.transmit(channel_id, "system", "@archon context needed")
    await bus.transmit(channel_id, "system", "@conclave deliberation needed")

    active_agents = bus.spawner.get_active_agents(channel_id)
    assert len(active_agents) == 2

    messages = bus.history(channel_id)
    rejection_messages = [
        msg for msg in messages if "max agents" in msg.content.lower()
    ]
    assert len(rejection_messages) == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_spawn_isolation_between_channels(mock_agent):
    """Test spawned agents are isolated per channel."""
    bus = Bus(max_agents=5, enable_storage=False)

    await bus.transmit("squad-alpha", "system", "@zealot review needed")
    await bus.transmit("squad-beta", "system", "@archon context needed")

    alpha_agents = bus.spawner.get_active_agents("squad-alpha")
    beta_agents = bus.spawner.get_active_agents("squad-beta")

    assert len(alpha_agents) == 1
    assert len(beta_agents) == 1
    assert alpha_agents[0].agent_type == "zealot"
    assert beta_agents[0].agent_type == "archon"

    alpha_channel_agents = bus.channels["squad-alpha"]
    beta_channel_agents = bus.channels["squad-beta"]

    assert alpha_agents[0].agent_id in alpha_channel_agents
    assert alpha_agents[0].agent_id not in beta_channel_agents
    assert beta_agents[0].agent_id in beta_channel_agents
    assert beta_agents[0].agent_id not in alpha_channel_agents


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unknown_agent_type_handling(mock_agent):
    """Test graceful handling of unknown agent types."""
    bus = Bus(max_agents=5, enable_storage=False)

    channel_id = "squad-unknown"

    await bus.transmit(channel_id, "system", "@unknown_agent help needed")

    spawned_agents = bus.spawner.get_active_agents(channel_id)
    assert len(spawned_agents) == 0

    messages = bus.history(channel_id)
    fallback_messages = [
        msg for msg in messages if "unknown agent type" in msg.content.lower()
    ]
    assert len(fallback_messages) == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_spawn_coordination_background_task(mock_agent):
    """Test spawned agents start coordination in background."""
    bus = Bus(max_agents=5, enable_storage=False)

    channel_id = "squad-coordination"

    await bus.transmit(channel_id, "system", "@zealot architectural review needed")

    spawned_agents = bus.spawner.get_active_agents(channel_id, "zealot")
    assert len(spawned_agents) == 1

    messages = bus.history(channel_id)
    spawn_messages = [msg for msg in messages if "Spawned" in msg.content]
    assert len(spawn_messages) == 1

    # New architecture does not auto-run spawned agents
    agent_messages = [msg for msg in messages if msg.sender.startswith("zealot-")]
    assert len(agent_messages) == 0
