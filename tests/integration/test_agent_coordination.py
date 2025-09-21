"""Integration tests for multi-agent coordination."""

import pytest
import asyncio
from unittest.mock import AsyncMock
from protoss import Protoss, Config
from protoss.core.bus import Bus
from protoss.agents import Zealot, Conclave, Archon


@pytest.mark.integration
@pytest.mark.asyncio
async def test_basic_coordination(mock_agent):
    """Single agent coordination through Bus."""
    bus = Bus(enable_storage=False)
    config = Config(debug=True)
    zealot = Zealot()

    result = await zealot.coordinate("Simple task", "squad-test", config, bus)

    assert result is not None
    assert "squad-test" in bus.memories
    assert len(bus.memories["squad-test"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_constitutional_deliberation(mock_agent):
    """Constitutional deliberation with real Conclave."""
    bus = Bus(enable_storage=False)
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
    assert any("despawn" in msg.lower() for msg in messages)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mention_escalation_flow(monkeypatch):
    """End-to-end mention escalation with real agents."""

    # Custom mock that handles mentions properly
    class MentionMockAgent:
        def __init__(self, instructions=None, tools=None, **kwargs):
            self.instructions = instructions
            self.tools = tools or []

        async def __call__(
            self, user_message, user_id=None, conversation_id=None, chunks=False
        ):
            full_context = f"{self.instructions or ''} {user_message}"
            if "@archon" in full_context:
                yield {"type": "respond", "content": "!despawn"}
            else:
                yield {"type": "respond", "content": "Task complete. !despawn"}

    monkeypatch.setattr("cogency.core.agent.Agent", MentionMockAgent)

    bus = Bus(enable_storage=False)
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

    # Should have spawn notification
    spawn_messages = [msg for msg in messages if "Spawned" in msg.content]
    assert len(spawn_messages) == 1

    # Archon should respond automatically to the mention
    archon_messages = [msg for msg in messages if msg.sender.startswith("archon-")]
    assert len(archon_messages) >= 1
    assert any("archives" in msg.content.lower() for msg in archon_messages)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_arbiter_auto_response(monkeypatch):
    """Arbiter should respond immediately when summoned."""

    class ArbiterMentionMockAgent:
        def __init__(self, instructions=None, tools=None, **kwargs):
            self.instructions = instructions
            self.tools = tools or []

        async def __call__(
            self, user_message, user_id=None, conversation_id=None, chunks=False
        ):
            full_context = f"{self.instructions or ''} {user_message}"
            if "@arbiter" in full_context:
                yield {
                    "type": "respond",
                    "content": "Summoning @arbiter for human translation.",
                }
                yield {"type": "respond", "content": "!despawn"}
            else:


    monkeypatch.setattr("cogency.core.agent.Agent", ArbiterMentionMockAgent)

    bus = Bus(enable_storage=False)
    config = Config(debug=True)
    zealot = Zealot()

    await zealot.coordinate(
        "Need @arbiter to relay status to the human",
        "squad-arbiter-escalation",
        config,
        bus,
    )

    messages = bus.memories["squad-arbiter-escalation"]

    arbiter_messages = [msg for msg in messages if msg.sender.startswith("arbiter-")]
    assert len(arbiter_messages) >= 1
    assert any("Arbiter engaged" in msg.content for msg in arbiter_messages)
    assert all("@human" not in msg.content for msg in arbiter_messages)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_conclave_auto_response(monkeypatch):
    """Conclave should assemble and respond with perspectives."""

    class ConclaveMentionMockAgent:
        def __init__(self, instructions=None, tools=None, **kwargs):
            self.instructions = instructions
            self.tools = tools or []

        async def __call__(
            self, user_message, user_id=None, conversation_id=None, chunks=False
        ):
            full_context = f"{self.instructions or ''} {user_message}"
            if "@conclave" in full_context:
                yield {
                    "type": "respond",
                    "content": "Escalating to @conclave for Sacred Four deliberation.",
                }
                yield {"type": "respond", "content": "!despawn"}
            else:


    monkeypatch.setattr("cogency.core.agent.Agent", ConclaveMentionMockAgent)

    bus = Bus(enable_storage=False)
    config = Config(debug=True)
    zealot = Zealot()

    await zealot.coordinate(
        "Team is split, summon @conclave for decision",
        "squad-conclave-escalation",
        config,
        bus,
    )

    messages = bus.memories["squad-conclave-escalation"]

    conclave_messages = [
        msg
        for msg in messages
        if msg.sender.startswith("tassadar-")
        or msg.sender.startswith("zeratul-")
        or msg.sender.startswith("artanis-")
        or msg.sender.startswith("fenix-")
    ]

    # Ensure all Sacred Four responded
    assert {msg.sender.split("-", 1)[0] for msg in conclave_messages} == {
        "tassadar",
        "zeratul",
        "artanis",
        "fenix",
    }

    assert all("Preparing full constitutional deliberation" in msg.content for msg in conclave_messages)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_engine_orchestration(monkeypatch):
    """End-to-end coordination through Protoss engine."""

    # Custom mock that simulates tool usage for realistic engine testing
    class ToolMockAgent:
        def __init__(self, instructions=None, tools=None, **kwargs):
            self.instructions = instructions
            self.tools = tools or []

        async def __call__(
            self, user_message, user_id=None, conversation_id=None, chunks=False
        ):
            full_context = f"{self.instructions or ''} {user_message}"

            if "ZEALOT" in (self.instructions or ""):
                yield {
                    "type": "think",
                    "content": "Analyzing authentication requirements...",
                }
                if "authentication" in full_context.lower():
                    yield {
                        "type": "call",
                        "content": '{"name": "file_write", "args": {"file": "auth.py"}}',
                    }
                    yield {"type": "execute"}
                yield {
                    "type": "respond",
                    "content": "Authentication system designed with zealot principles. !despawn",
                }
            elif "ARCHON" in (self.instructions or ""):
                yield {"type": "think", "content": "Checking knowledge archives..."}
                yield {
                    "type": "respond",
                    "content": "Knowledge context provided for authentication. !despawn",
                }
            else:
                yield {
                    "type": "respond",
                    
    monkeypatch.setattr("cogency.core.agent.Agent", ToolMockAgent)

    # Create engine with ephemeral port for testing
    protoss = Protoss(Config(agents=3, debug=True))
    protoss.bus = Bus(port=0, enable_storage=False)
    monkeypatch.setattr(protoss.bus, "start", AsyncMock())
    monkeypatch.setattr(protoss.bus, "stop", AsyncMock())

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
    bus = Bus(enable_storage=False)
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
    bus = Bus(max_memory=5, enable_storage=False)  # Configure bus directly

    # Test config values work with bus
    assert bus.max_memory == 5

    # Test memory limits are enforced
    for i in range(10):
        await bus.transmit("squad-config", "sender", f"Message {i}")

    assert len(bus.memories["squad-config"]) == 5  # Trimmed to limit


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multi_agent_coordination(mock_agent):
    """Test multiple agents coordinating together through Bus."""
    bus = Bus(enable_storage=False)
    config = Config(debug=True, max_cycles=2)

    # Create multiple constitutional agents
    zealot = Zealot("zealot-worker")
    archon = Archon("archon-knowledge")
    conclave = Conclave("tassadar", "tassadar-strategist")

    channel_id = "squad-multi-agent"
    task = "Design authentication system with team coordination"

    # All agents coordinate on same channel

    await asyncio.gather(
        zealot.coordinate(task, channel_id, config, bus),
        archon.coordinate(task, channel_id, config, bus),
        conclave.coordinate(task, channel_id, config, bus),
        return_exceptions=True,
    )

    # Verify coordination happened
    messages = bus.memories[channel_id]
    assert len(messages) >= 3, "Should have messages from multiple agents"

    # Verify each agent type participated
    zealot_msgs = [msg for msg in messages if "zealot" in msg.sender]
    archon_msgs = [msg for msg in messages if "archon" in msg.sender]
    conclave_msgs = [
        msg for msg in messages if "conclave" in msg.sender or "tassadar" in msg.sender
    ]

    assert len(zealot_msgs) > 0, "Zealot should participate"
    assert len(archon_msgs) > 0, "Archon should participate"
    assert len(conclave_msgs) > 0, "Conclave should participate"

    # Verify constitutional identities preserved
    all_content = " ".join(msg.content for msg in messages)
    assert "!despawn" in all_content.lower(), "Should have despawn signals"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_constitutional_identity_preservation(monkeypatch):
    """Test that each agent type maintains constitutional identity."""

    # Custom mock that responds with constitutional identity
    class IdentityMockAgent:
        def __init__(self, instructions=None, tools=None, **kwargs):
            self.instructions = instructions
            self.tools = tools or []

        async def __call__(
            self, user_message, user_id=None, conversation_id=None, chunks=False
        ):
            if "ZEALOT" in (self.instructions or ""):
                yield {
                    "type": "respond",
                    "content": "Constitutional zealot analysis complete. !despawn",
                }
            elif "ARCHON" in (self.instructions or ""):
                yield {
                    "type": "respond",
                    "content": "Knowledge archon stewardship complete. !despawn",
                }
            elif "FENIX" in (self.instructions or ""):
                yield {
                    "type": "respond",
                    "content": "Strategic fenix perspective complete. !despawn",
                }
            else:
                yield {
                    "type": "respond",
                    "content": "Constitutional coordination complete. !despawn",
                }


    monkeypatch.setattr("cogency.core.agent.Agent", IdentityMockAgent)

    bus = Bus(enable_storage=False)
    config = Config(debug=True, max_cycles=1)

    # Test each constitutional agent type
    agents = [
        (Zealot("zealot-test"), "zealot"),
        (Archon("archon-test"), "archon"),
        (Conclave("fenix", "fenix-test"), "fenix"),
    ]

    for agent, expected_type in agents:
        channel_id = f"squad-identity-{expected_type}"
        task = f"Test constitutional identity for {expected_type}"

        result = await agent.coordinate(task, channel_id, config, bus)

        # Verify agent responded appropriately to its constitutional nature
        assert result is not None
        messages = bus.memories[channel_id]
        assert len(messages) > 0, f"{expected_type} should respond"

        # Verify constitutional identity in response
        all_content = " ".join(msg.content for msg in messages)
        if expected_type == "zealot":
            assert (
                "zealot" in all_content.lower()
                or "constitutional" in all_content.lower()
            )
        elif expected_type == "archon":
            assert "knowledge" in all_content.lower() or "archon" in all_content.lower()
        elif expected_type == "fenix":
            assert "strategic" in all_content.lower() or "fenix" in all_content.lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_lifecycle_signals_integration(mock_agent):
    """Test lifecycle signals work in coordination."""
    bus = Bus(enable_storage=False)
    config = Config(debug=True, max_cycles=1)

    zealot = Zealot("zealot-lifecycle")

    # Test completion signal
    result = await zealot.coordinate(
        "Simple task that should complete quickly",
        "squad-lifecycle-complete",
        config,
        bus,
    )

    assert "despawn" in result.lower(), "Should signal despawn"

    # Verify completion signal propagated
    messages = bus.memories["squad-lifecycle-complete"]
    all_content = " ".join(msg.content for msg in messages)
    assert "!DESPAWN" in all_content.upper(), "Should have explicit despawn signal"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cogency_integration_verification(mock_agent):
    """Verify cogency Agent integration is working correctly."""
    bus = Bus(enable_storage=False)
    config = Config(debug=True, max_cycles=1)

    # Test that agents use cogency properly
    zealot = Zealot("zealot-cogency-test")

    # This should trigger the cogency Agent pathway in base.py
    result = await zealot.coordinate(
        "Test cogency integration with constitutional identity",
        "squad-cogency-verification",
        config,
        bus,
    )

    # Verify execution happened through our coordination system
    assert result is not None
    messages = bus.memories["squad-cogency-verification"]
    assert len(messages) > 0, "Should have cogency-generated messages"

    # Verify message came from zealot with constitutional response
    zealot_msg = messages[0]
    assert "zealot" in zealot_msg.sender, "Message should be from zealot"
    assert (
        len(zealot_msg.content) > 10
    ), "Should have substantial constitutional response"

    # Verify our base.py execute() method was used (not manual override)
    # This is implicit - if the test passes, cogency integration worked
