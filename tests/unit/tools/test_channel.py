"""Unit tests for channel coordination tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.protoss.tools.channel import ChannelList, ChannelRead, ChannelSpawn


@pytest.fixture
def mock_bus():
    bus = MagicMock()
    bus.storage = MagicMock()
    bus.get_history = AsyncMock()
    bus.storage.get_channels = AsyncMock()
    return bus


@pytest.fixture
def mock_protoss():
    protoss = MagicMock()
    protoss.spawn_agent = AsyncMock()
    return protoss


@pytest.mark.asyncio
async def test_list_empty(mock_bus):
    mock_bus.storage.get_channels.return_value = []

    tool = ChannelList(mock_bus)
    result = await tool.execute()

    assert result.outcome == "No active channels"
    assert result.content is None


@pytest.mark.asyncio
async def test_list_channels(mock_bus):
    mock_bus.storage.get_channels.return_value = ["main", "research", "build"]

    tool = ChannelList(mock_bus)
    result = await tool.execute()

    assert result.outcome == "Found 3 active channels"
    assert "#main" in result.content
    assert "#research" in result.content
    assert "#build" in result.content


@pytest.mark.asyncio
async def test_read_empty_channel(mock_bus):
    mock_bus.get_history.return_value = []

    tool = ChannelRead(mock_bus)
    result = await tool.execute(channel="research")

    assert result.outcome == "Channel #research not found or empty"
    mock_bus.get_history.assert_called_once_with(channel="research")


@pytest.mark.asyncio
async def test_read_channel_transcript(mock_bus):
    history = [
        {"sender": "zealot", "content": "I'll handle the API"},
        {"sender": "sentinel", "content": "I'll write tests"},
    ]
    mock_bus.get_history.return_value = history

    tool = ChannelRead(mock_bus)
    result = await tool.execute(channel="research")

    assert result.outcome == "Read 2 messages from #research"
    assert "zealot: I'll handle the API" in result.content
    assert "sentinel: I'll write tests" in result.content


@pytest.mark.asyncio
async def test_read_no_channel_name(mock_bus):
    tool = ChannelRead(mock_bus)
    result = await tool.execute(channel="")

    assert result.outcome == "Channel name required"


@pytest.mark.asyncio
async def test_spawn_success(mock_bus, mock_protoss):
    mock_bus.storage.get_channels.return_value = ["main"]
    mock_bus.send = AsyncMock()

    tool = ChannelSpawn(mock_bus, mock_protoss, parent_channel="main")
    result = await tool.execute(channel="research", task="Compare testing frameworks")

    assert (
        result.outcome
        == "Spawned #research [zealot, sentinel, harbinger] - task: Compare testing frameworks"
    )

    # Verify task sent with spawn context
    mock_bus.send.assert_called_once()
    call_args = mock_bus.send.call_args
    assert call_args[0][0] == "human"
    assert "Compare testing frameworks" in call_args[0][1]
    assert "[Active channels:" in call_args[0][1]
    assert "[You are in: #research]" in call_args[0][1]
    assert call_args[0][2] == "research"

    # Verify agents spawned
    assert mock_protoss.spawn_agent.call_count == 3
    mock_protoss.spawn_agent.assert_any_call(
        "zealot", channel="research", parent="main"
    )
    mock_protoss.spawn_agent.assert_any_call(
        "sentinel", channel="research", parent="main"
    )
    mock_protoss.spawn_agent.assert_any_call(
        "harbinger", channel="research", parent="main"
    )


@pytest.mark.asyncio
async def test_spawn_channel_exists(mock_bus, mock_protoss):
    mock_bus.storage.get_channels.return_value = ["main", "research"]

    tool = ChannelSpawn(mock_bus, mock_protoss)
    result = await tool.execute(channel="research", task="Some task")

    assert "Error: #research already exists" in result.outcome
    assert "#main" in result.outcome
    assert "#research" in result.outcome
    mock_protoss.spawn_agent.assert_not_called()


@pytest.mark.asyncio
async def test_spawn_no_channel_name(mock_bus, mock_protoss):
    tool = ChannelSpawn(mock_bus, mock_protoss, parent_channel="main")
    result = await tool.execute(channel="", task="Some task")

    assert result.outcome == "Channel name required"


@pytest.mark.asyncio
async def test_spawn_no_task(mock_bus, mock_protoss):
    tool = ChannelSpawn(mock_bus, mock_protoss, parent_channel="main")
    result = await tool.execute(channel="research", task="")

    assert result.outcome == "Task description required"
