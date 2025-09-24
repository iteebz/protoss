"""Bus coordination contract tests."""

import json
import pytest
from unittest.mock import AsyncMock, patch
from protoss.core.protocols import Mention

from protoss.core.bus import Bus, Event, Coordination
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


@pytest.mark.asyncio
@patch("protoss.core.gateway.spawn_agent")
@patch("protoss.core.gateway.should_spawn")
async def test_bus_spawns_agent_on_mention(mock_should_spawn, mock_spawn):
    """Bus triggers gateway spawn on @mention."""
    bus = Bus()
    mock_spawn.return_value = AsyncMock()
    mock_should_spawn.return_value = True
    bus.transmit = AsyncMock()  # Mock transmit to avoid broadcast side-effects

    # Create proper Mention object
    mention = Mention(agent_name="zealot")

    message = Message(
        channel="test_channel",
        sender="user",
        event={"content": "@zealot do the thing"},
        msg_type="agent_message",
        coordination_id="coord-123",
    )
    message.signals = [mention]
    event = Event(
        type="agent_message",
        channel="test_channel",
        sender="user",
        timestamp=message.timestamp,
        payload=message.event,
        message=message,
        coordination_id="coord-123",
        content="@zealot do the thing",
        signals=message.signals,
    )

    # We are testing the private method directly as it contains the core logic
    await bus._dispatch_mentions(event)

    mock_spawn.assert_called_once_with("zealot", "test_channel", bus.url)


@pytest.mark.asyncio
async def test_bus_completes_coordination():
    """Bus marks coordination as complete when all agents despawn."""
    bus = Bus()
    bus.transmit = AsyncMock()  # Mock transmit to capture the completion event

    coord_id = "coord-to-complete"
    channel_id = "test_channel"

    # Simulate starting a coordination and spawning an agent
    bus.coordinations[coord_id] = Coordination(
        channels={channel_id: {"zealot-1"}},
        status="active",
        had_agents=True,
    )

    # Simulate the agent despawning
    message = Message(
        channel=channel_id,
        sender="zealot-1",
        event={"agent_id": "zealot-1"},
        msg_type="agent_despawn",
        coordination_id=coord_id,
    )
    event = Event(
        type="agent_despawn",
        channel=channel_id,
        sender="zealot-1",
        timestamp=message.timestamp,
        payload=message.event,
        message=message,
        coordination_id=coord_id,
        content="",
        signals=[],
    )
    await bus._update_lifecycle(event)

    assert bus.coordinations[coord_id].status == "complete"
    bus.transmit.assert_called_with(
        channel=channel_id,
        sender="system",
        event_type="coordination_complete",
        coordination_id=coord_id,
        event_payload={"result": "Coordination finished successfully."},
    )


@pytest.mark.asyncio
@patch("protoss.core.bus.Bus._probe_create_channel", new_callable=AsyncMock)
async def test_bus_handles_probe_command(mock_create_channel):
    """Bus correctly parses and executes a probe command."""
    bus = Bus()

    probe_command = {
        "action": "create_channel",
        "description": "a new task channel",
        "instruction": "@zealot begin",
    }

    # Create proper Mention object
    probe_mention = Mention(agent_name="probe")

    message = Message(
        channel="request_channel",
        sender="user",
        event={"content": json.dumps(probe_command)},
        msg_type="agent_message",
        coordination_id="coord-123",
    )
    message.signals = [probe_mention]
    event = Event(
        type="agent_message",
        channel="request_channel",
        sender="user",
        timestamp=message.timestamp,
        payload=message.event,
        message=message,
        coordination_id="coord-123",
        content=json.dumps(probe_command),
        signals=message.signals,
    )
    await bus._handle_probe_command(event)

    mock_create_channel.assert_called_once_with(probe_command, "coord-123")
