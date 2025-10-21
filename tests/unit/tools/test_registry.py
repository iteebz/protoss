"""Unit tests for protoss_tools registry."""

from unittest.mock import MagicMock

from protoss.tools import protoss_tools


def test_base_tools():
    tools = protoss_tools()
    assert len(tools) == 9


def test_channel_tools():
    mock_bus = MagicMock()
    mock_protoss = MagicMock()

    tools = protoss_tools(bus=mock_bus, protoss=mock_protoss, parent_channel="main")

    assert len(tools) == 12

    tool_names = [t.name for t in tools]
    assert "channel_list" in tool_names
    assert "channel_read" in tool_names
    assert "channel_spawn" in tool_names


def test_channel_tools_init():
    mock_bus = MagicMock()
    mock_protoss = MagicMock()

    tools = protoss_tools(bus=mock_bus, protoss=mock_protoss, parent_channel="main")

    channel_tools = {t.name: t for t in tools if t.name.startswith("channel_")}

    assert channel_tools["channel_list"].bus is mock_bus
    assert channel_tools["channel_read"].bus is mock_bus
    assert channel_tools["channel_spawn"].bus is mock_bus
    assert channel_tools["channel_spawn"].protoss is mock_protoss
    assert channel_tools["channel_spawn"].parent_channel == "main"
