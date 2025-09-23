"""Bus coordination contract tests."""

import pytest
from unittest.mock import AsyncMock

from protoss.core.bus import Bus
from protoss.core.message import Message


@pytest.mark.asyncio
async def test_bus_stores_channel_history():
    """Bus appends message to channel history."""
    bus = Bus(port=8888)
    bus._send = AsyncMock()
    channel_id = "history_channel"
    message = Message(channel_id, "sender", event={"content": "history test"})

    await bus._broadcast(message)

    assert channel_id in bus.channels
    assert len(bus.channels[channel_id].history) == 1
    assert bus.channels[channel_id].history[0] == message


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
