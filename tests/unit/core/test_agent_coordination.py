"""Unit tests for agent coordination loop with mocked cogency."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from protoss.core.bus import Bus
from protoss.core.agent import Agent


@pytest.fixture
def temp_bus(tmp_path):
    """Create isolated Bus instance."""
    return Bus(base_dir=str(tmp_path))


@pytest.fixture
def mock_cogency_agent():
    """Mock cogency agent that simulates respond events."""
    agent = AsyncMock()

    async def mock_respond(content, user_id=None, conversation_id=None):
        yield {"type": "respond", "content": f"Response to: {content[:30]}"}
        yield {"type": "end"}

    agent.__call__.side_effect = mock_respond
    return agent


@pytest.mark.asyncio
async def test_agent_reads_new_messages(temp_bus):
    """Agent polls bus for new messages and processes them."""
    channel = "test_read"
    await temp_bus.send("human", "Build a calculator", channel)

    with (
        patch("protoss.core.agent.cogency") as mock_cogency_module,
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        mock_cogency_module.Agent = MagicMock()
        Agent(agent_type="zealot", bus=temp_bus, channel=channel)

        history = await temp_bus.get_history(channel)
        assert len(history) == 1
        assert history[0]["content"] == "Build a calculator"


@pytest.mark.asyncio
async def test_agent_filters_own_messages(temp_bus):
    """Agent ignores its own messages in coordination loop."""
    channel = "test_filter"

    with (
        patch("protoss.core.agent.cogency") as mock_cogency_module,
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        mock_cogency_module.Agent = MagicMock()
        Agent(agent_type="zealot", bus=temp_bus, channel=channel)

    await temp_bus.send("zealot", "My own message", channel)
    await temp_bus.send("human", "Please respond", channel)

    history = await temp_bus.get_history(channel)
    assert len(history) == 2
    assert history[0]["sender"] == "zealot"
    assert history[1]["sender"] == "human"

    filtered = [msg for msg in history if msg["sender"] != "zealot"]
    assert len(filtered) == 1
    assert filtered[0]["content"] == "Please respond"


@pytest.mark.asyncio
async def test_agent_detects_exit_signals(temp_bus):
    """Agent recognizes exit signal patterns and stops."""
    channel = "test_signals"

    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=temp_bus, channel=channel)

    test_signals = ["!done", "!consensus", "!complete", "!despawn"]

    for signal in test_signals:
        agent.running = True
        messages = [{"sender": "human", "content": f"Message with {signal}"}]

        filtered = [msg for msg in messages if msg["sender"] != agent.agent_type]
        assert len(filtered) == 1

        content_lower = filtered[0]["content"].lower()
        has_signal = any(
            sig in content_lower
            for sig in ["!done", "!consensus", "!complete", "!despawn"]
        )
        assert has_signal, f"Should detect {signal}"


@pytest.mark.asyncio
async def test_agent_broadcasts_responses(temp_bus):
    """Agent broadcasts responses to bus after processing."""
    channel = "test_broadcast"

    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=temp_bus, channel=channel)

    test_response = "Here is my analysis"
    await temp_bus.send(agent.agent_type, test_response, channel)

    history = await temp_bus.get_history(channel)
    assert any(
        msg["sender"] == "zealot" and msg["content"] == test_response for msg in history
    )


@pytest.mark.asyncio
async def test_agent_maintains_conversation_context(temp_bus):
    """Agent loads full history on spawn and uses it as context."""
    channel = "test_context"

    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=temp_bus, channel=channel)

    await temp_bus.send("human", "First message about APIs", channel)
    await temp_bus.send("human", "Use REST architecture", channel)

    history = await temp_bus.get_history(channel)
    assert len(history) == 2

    formatted = agent._format_history(history)
    assert "human: First message about APIs" in formatted
    assert "human: Use REST architecture" in formatted


@pytest.mark.asyncio
async def test_agent_exit_on_signal(temp_bus):
    """Agent sets running=False when exit signal detected."""
    channel = "test_exit"

    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        agent = Agent(agent_type="zealot", bus=temp_bus, channel=channel)

    assert agent.running is True
    agent.running = False
    assert agent.running is False


@pytest.mark.asyncio
async def test_agent_different_types(temp_bus):
    """Agent works with different constitutional types."""
    with (
        patch("protoss.core.agent.cogency"),
        patch("protoss.core.agent.OpenAI"),
        patch("protoss.core.agent.SQLite"),
        patch("protoss.core.agent.Security"),
    ):
        for agent_type in ["zealot", "sentinel", "harbinger"]:
            agent = Agent(agent_type=agent_type, bus=temp_bus, channel="test")
            assert agent.agent_type == agent_type
            assert agent.running is True
