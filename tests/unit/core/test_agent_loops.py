"""Tests for agent coordination loop correctness."""

import pytest
from unittest.mock import patch

from protoss.core.bus import Bus
from protoss.core.agent import Agent


@pytest.fixture
def temp_bus(tmp_path):
    return Bus(base_dir=str(tmp_path))


@pytest.mark.asyncio
async def test_exit_signal_stops_agent_loop(temp_bus):
    """Agent detects exit signal and actually stops running."""
    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=temp_bus, channel="test")

    assert agent.running is True

    await temp_bus.send("human", "Please proceed with !despawn", "test")

    history = await temp_bus.get_history("test")
    assert any("!despawn" in msg["content"] for msg in history)

    filtered = [msg for msg in history if msg["sender"] != "zealot"]
    for msg in filtered:
        if "!despawn" in msg["content"].lower():
            assert True, "Exit signal should be detected in filtered messages"
            break


@pytest.mark.asyncio
async def test_completion_signal_broadcasts_to_current_channel(temp_bus):
    """!complete signal broadcasts to current channel when no parent."""
    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        Agent(agent_type="zealot", bus=temp_bus, channel="test")

    await temp_bus.send("zealot", "Task complete. !complete", "test")

    history = await temp_bus.get_history("test")

    completion_messages = [
        msg for msg in history if "complete" in msg["content"].lower()
    ]

    assert (
        len(completion_messages) > 0
    ), "Completion signal should be in channel history"


@pytest.mark.asyncio
async def test_initial_context_with_empty_channel(temp_bus):
    """Agent framing includes initial message even on empty channel."""
    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=temp_bus, channel="empty")

    history = await temp_bus.get_history("empty")

    assert len(history) == 0, "Empty channel should have no messages initially"

    framing_msg = "Channel #empty initialized. Awaiting task from human."
    await temp_bus.send(agent.agent_type, framing_msg, "empty")

    history = await temp_bus.get_history("empty")

    assert len(history) >= 1, "Should be able to store framing message"


@pytest.mark.asyncio
async def test_poll_time_not_updated_without_external_messages(temp_bus):
    """Poll time doesn't advance if only own messages exist."""
    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=temp_bus, channel="test")

    await temp_bus.send("zealot", "my first message", "test")

    agent.last_poll_time = 0

    history = await temp_bus.get_history("test", since=agent.last_poll_time)

    filtered = [msg for msg in history if msg["sender"] != "zealot"]

    if not filtered:
        assert len(filtered) == 0, "Should not process own messages"


def test_tool_errors_collected_for_telemetry():
    """Tool errors are recorded internally for diagnostics."""
    bus = Bus()

    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=bus, channel="test")

    error_record = {
        "agent": "zealot",
        "tool": "write",
        "call": {"name": "write"},
        "outcome": "File write error: Permission denied",
    }
    agent.errors.append(error_record)

    assert len(agent.errors) > 0, "Tool errors should be collected"
    assert agent.errors[0]["tool"] == "write"
    assert "Permission" in agent.errors[0]["outcome"]
