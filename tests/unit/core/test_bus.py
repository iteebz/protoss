"""Bus coordination tests."""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from protoss.core.bus import Bus
from protoss.core.message import Message
from protoss.core.server import Server


@pytest.mark.asyncio
async def test_bus_broadcasts_to_subscribers():
    """Bus broadcasts message to all subscribers except sender."""
    mock_server = AsyncMock(spec=Server)
    with patch("protoss.core.server.Server", return_value=mock_server):
        bus = Bus(port=8888)
        bus.server = mock_server

        channel_id = "test_channel"
        sender_id = "sender_agent"
        subscriber1 = "sub_agent1"
        subscriber2 = "sub_agent2"

        bus.register(channel_id, sender_id)
        bus.register(channel_id, subscriber1)
        bus.register(channel_id, subscriber2)

        message = Message(channel_id, sender_id, event={"content": "test"})

        await bus._broadcast(message)

        assert mock_server.send.call_count == 2


@pytest.mark.asyncio
async def test_bus_stores_channel_history():
    """Bus appends message to channel history."""
    with patch("protoss.core.server.Server", return_value=AsyncMock(spec=Server)):
        bus = Bus(port=8888)
        channel_id = "history_channel"
        message = Message(channel_id, "sender", event={"content": "history test"})

        await bus._broadcast(message)

        assert channel_id in bus.channels
        assert len(bus.channels[channel_id].history) == 1
        assert bus.channels[channel_id].history[0] == message


@pytest.mark.asyncio
async def test_bus_lifecycle(mock_server):
    """Bus starts and stops server correctly."""
    mock_server.on_message = Mock()
    mock_server.on_connect = Mock()
    mock_server.on_disconnect = Mock()

    with patch("protoss.core.bus.Server", return_value=mock_server) as MockServerClass:
        bus = Bus(port=9999)
        await bus.start()

        MockServerClass.assert_called_once_with(9999)
        mock_server.on_message.assert_called_once_with(bus._message)
        mock_server.on_connect.assert_called_once_with(bus._connect)
        mock_server.on_disconnect.assert_called_once_with(bus._disconnect)
        mock_server.start.assert_called_once()

        await bus.stop()
        mock_server.stop.assert_called_once()


@pytest.mark.asyncio
async def test_bus_tracks_active_agents():
    """Bus tracks active agents for spawning decisions."""
    bus = Bus()

    bus.register("channel1", "zealot-1")
    bus.register("channel1", "archon-1")
    bus.register("channel2", "zealot-2")

    assert "zealot-1" in bus.active_agents["channel1"]
    assert "archon-1" in bus.active_agents["channel1"]
    assert "zealot-2" in bus.active_agents["channel2"]

    bus.deregister("zealot-1")
    assert "zealot-1" not in bus.active_agents["channel1"]
