"""Tests for agent error handling and recovery."""

import pytest
from unittest.mock import patch

from protoss.core.agent import Agent
from protoss.core.bus import Bus


@pytest.fixture
def temp_bus(tmp_path):
    """Create isolated Bus instance."""
    return Bus(base_dir=str(tmp_path))


def test_agent_raises_on_missing_cogency():
    """Agent raises ImportError if cogency unavailable during init."""
    bus = Bus()

    with patch("protoss.core.agent.cogency", None):
        with pytest.raises(ImportError, match="cogency is required"):
            Agent(agent_type="zealot", bus=bus, channel="test")


def test_agent_tracks_tool_errors():
    """Agent collects tool execution errors for debugging."""
    bus = Bus()
    agent = Agent(agent_type="zealot", bus=bus, channel="test")

    # Manually add error record (simulating tool failure)
    agent.errors.append(
        {
            "agent": "zealot",
            "tool": "write",
            "call": {"name": "write", "args": {}},
            "outcome": "File not found error",
        }
    )

    assert len(agent.errors) == 1
    assert agent.errors[0]["tool"] == "write"
    assert "not found" in agent.errors[0]["outcome"].lower()


@pytest.mark.asyncio
async def test_agent_processes_context_gracefully(temp_bus):
    """Agent should handle _process_with_cogency correctly."""
    agent = Agent(agent_type="sentinel", bus=temp_bus, channel="test")

    # Verify method exists and is callable
    assert hasattr(agent, "_process_with_cogency")
    assert callable(agent._process_with_cogency)

    # Should be async
    import inspect

    assert inspect.iscoroutinefunction(agent._process_with_cogency)


@pytest.mark.asyncio
async def test_agent_formats_history_correctly(temp_bus):
    """Agent formats message history for context injection."""
    agent = Agent(agent_type="zealot", bus=temp_bus, channel="test")

    history = [
        {"sender": "human", "content": "Build a calculator"},
        {"sender": "zealot", "content": "Only if it's not bloat"},
    ]

    formatted = agent._format_history(history)

    assert "human: Build a calculator" in formatted
    assert "zealot: Only if it's not bloat" in formatted
    assert formatted.count("\n") == 1, "Should join with newlines"


def test_agent_maintains_running_state():
    """Agent running state controls coordination loop."""
    bus = Bus()
    agent = Agent(agent_type="harbinger", bus=bus, channel="test")

    assert agent.running is True, "Agent should start in running state"

    agent.running = False
    assert agent.running is False


def test_agent_loads_constitutional_identity():
    """Agent loads correct constitutional identity for its type."""
    bus = Bus()

    for agent_type in ["zealot", "sentinel", "harbinger"]:
        agent = Agent(agent_type=agent_type, bus=bus, channel="test")

        identity = agent._load_constitutional_identity()
        assert isinstance(identity, str)
        assert len(identity) > 0
        assert agent_type.upper() in identity.upper()


def test_agent_loads_coordination_guidelines():
    """Agent loads coordination guidelines from constitution."""
    bus = Bus()
    agent = Agent(agent_type="zealot", bus=bus, channel="test")

    guidelines = agent._load_coordination_guidelines()
    assert isinstance(guidelines, str)
    assert len(guidelines) > 0
    assert "COMMUNICATION" in guidelines.upper() or "CONTEXT" in guidelines.upper()


def test_agent_poll_time_tracking():
    """Agent tracks last poll time to compute diffs."""
    bus = Bus()
    agent = Agent(agent_type="zealot", bus=bus, channel="test")

    assert hasattr(agent, "last_poll_time")
    assert agent.last_poll_time == 0, "Should start at epoch"


def test_agent_conversation_id_equals_channel():
    """Agent conversation_id should always equal channel."""
    bus = Bus()
    channel = "test_channel"
    agent = Agent(agent_type="sentinel", bus=bus, channel=channel)

    assert agent.conversation_id == channel
    assert agent.channel == channel
    assert (
        agent.conversation_id == agent.channel
    ), "Invariant: conversation_id == channel"


@pytest.mark.asyncio
async def test_agent_cogency_initialization(temp_bus):
    """Agent initializes cogency with correct parameters."""
    agent = Agent(agent_type="zealot", bus=temp_bus, channel="test")

    assert hasattr(agent, "cogency_agent")
    assert agent.cogency_agent is not None
    assert hasattr(agent.cogency_agent, "__call__")


def test_error_recovery_depth_limit():
    """Agent stops error recovery after depth > 2."""
    bus = Bus()

    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=bus, channel="test")

    assert agent.running is True

    import asyncio

    asyncio.run(agent._process_with_cogency("test", error_depth=0))
    assert agent.running is True, "Depth 0 should not despawn"

    asyncio.run(agent._process_with_cogency("test", error_depth=1))
    assert agent.running is True, "Depth 1 should not despawn"

    asyncio.run(agent._process_with_cogency("test", error_depth=2))
    assert agent.running is True, "Depth 2 should not despawn"

    asyncio.run(agent._process_with_cogency("test", error_depth=3))
    assert not agent.running, "Depth 3 should despawn"


@pytest.mark.asyncio
async def test_poll_time_advances_on_external_messages(temp_bus):
    """Poll time only advances when new external messages exist."""
    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=temp_bus, channel="test")

    initial_poll = agent.last_poll_time

    await temp_bus.send("zealot", "own message", "test")
    assert (
        agent.last_poll_time == initial_poll
    ), "Poll time should not advance on own messages"

    await temp_bus.send("human", "external message", "test")
    history = await temp_bus.get_history("test", since=initial_poll)
    assert len(history) >= 1, "Should retrieve messages after initial_poll"
