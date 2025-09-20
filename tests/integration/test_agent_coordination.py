"""Integration tests for multi-agent coordination."""

import pytest
from protoss import Protoss, Config
from protoss.core.bus import Bus
from protoss.agents import Zealot, Conclave, Archon


@pytest.mark.integration
@pytest.mark.asyncio
async def test_basic_coordination():
    """Single agent coordination through Bus."""
    bus = Bus()
    config = Config(debug=True)
    zealot = Zealot()

    result = await zealot.coordinate("Simple task", "squad-test", config, bus)

    assert result is not None
    assert "squad-test" in bus.memories
    assert len(bus.memories["squad-test"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_constitutional_deliberation():
    """Constitutional deliberation with real Conclave."""
    bus = Bus()
    config = Config(debug=True)
    conclave = Conclave("tassadar")

    result = await conclave.coordinate(
        "Should we implement microservices architecture?",
        "squad-deliberation",
        config,
        bus,
    )

    # Verify constitutional process
    assert result is not None
    assert "squad-deliberation" in bus.memories
    # Should contain constitutional reasoning
    messages = [msg.content for msg in bus.memories["squad-deliberation"]]
    assert any("complete" in msg.lower() for msg in messages)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mention_escalation_flow():
    """End-to-end mention escalation with real agents."""

    # Setup mention handler
    def archon_factory(mention, handler_id):
        return Archon()  # Real archon instance

    bus = Bus(mention_handlers={"archon": archon_factory})
    config = Config(debug=True)
    zealot = Zealot()

    # Trigger mention escalation
    await zealot.coordinate(
        "I need help @archon with this complex decision",
        "squad-escalation",
        config,
        bus,
    )

    # Verify escalation flow
    messages = bus.memories["squad-escalation"]
    assert len(messages) >= 2  # Original + archon response

    # Should have archon response
    archon_messages = [msg for msg in messages if "archon" in msg.sender]
    assert len(archon_messages) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_engine_orchestration():
    """End-to-end coordination through Protoss engine."""
    protoss = Protoss(Config(agents=3, debug=True))

    # Real multi-agent coordination
    result = await protoss("Design authentication system")

    # Verify orchestration worked
    assert result is not None
    assert "authentication" in result.lower()

    # Should have coordinated multiple agents
    status = await protoss.status()
    assert status["active_channels"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_bus_agent_integration():
    """Bus and agent integration without execute() dependency."""
    bus = Bus()
    Config(debug=True)
    Zealot()

    # Test agent can communicate through bus
    agent_id = "zealot-test"
    channel = "squad-integration"
    bus.register(channel, agent_id)
    await bus.transmit(channel, "system", "Test message")

    # Verify integration points work
    assert channel in bus.channels
    assert agent_id in bus.channels[channel]
    assert len(bus.memories[channel]) == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_config_bus_integration():
    """Config and Bus integration."""
    Config(debug=True)
    bus = Bus(max_memory=5)  # Configure bus directly

    # Test config values work with bus
    assert bus.max_memory == 5

    # Test memory limits are enforced
    for i in range(10):
        await bus.transmit("squad-config", "sender", f"Message {i}")

    assert len(bus.memories["squad-config"]) == 5  # Trimmed to limit
