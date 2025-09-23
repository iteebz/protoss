"""Protoss cathedral interface tests for the event-driven architecture."""

import pytest
from unittest.mock import AsyncMock, patch
import asyncio
import uuid

from protoss.core.protoss import Protoss
from protoss.core.message import Message  # Needed for Khala.receive mock


@pytest.fixture
def mock_bus():
    """Fixture to mock the Bus for isolated Protoss testing."""
    with patch("protoss.core.bus.Bus", autospec=True) as MockBus:
        mock_bus_instance = MockBus.return_value
        mock_bus_instance.start = AsyncMock()
        mock_bus_instance.stop = AsyncMock()
        yield mock_bus_instance


@pytest.fixture
def mock_khala():
    """Fixture to mock Khala for isolated Protoss testing."""
    with patch("protoss.core.khala.Khala", autospec=True) as MockKhala:
        mock_khala_instance = MockKhala.return_value
        mock_khala_instance.connect = AsyncMock()
        mock_khala_instance.disconnect = AsyncMock()
        mock_khala_instance.send = AsyncMock()
        # Mock receive to return a queue-like object for event streaming
        mock_khala_instance.receive = AsyncMock(side_effect=asyncio.Queue().get)
        yield mock_khala_instance


@pytest.mark.asyncio
async def test_protoss_init():
    """Protoss initializes with vision, port, and timeout."""
    vision = "test vision"
    port = 9999
    timeout = 60

    swarm = Protoss(vision, port=port, timeout=timeout)

    assert swarm.vision == vision
    assert swarm.port == port
    assert swarm.timeout == timeout
    assert isinstance(swarm.coordination_id, str)
    assert swarm.bus is None  # Bus is initialized in __aenter__
    assert swarm.khala is None  # Khala is initialized in __aenter__


@pytest.mark.asyncio
async def test_protoss_context_manager_lifecycle(mock_bus, mock_khala):
    """Protoss context manager handles Bus and Khala lifecycle, and seeds vision."""
    vision = "test vision for lifecycle"

    async with Protoss(vision) as swarm:
        mock_bus.start.assert_called_once()
        mock_khala.connect.assert_called_once_with(client_id="protoss_coordinator")
        mock_khala.send.assert_called_once()

        # Verify vision_seed event
        args, kwargs = mock_khala.send.call_args
        assert kwargs["channel"] == "nexus"
        assert kwargs["sender"] == "protoss"
        assert kwargs["event_type"] == "vision_seed"
        assert kwargs["coordination_id"] == swarm.coordination_id
        assert kwargs["event_payload"]["vision"] == vision
        assert (
            f"{vision} @arbiter" in kwargs["content"]
        )  # Check content for signal parsing

    mock_khala.disconnect.assert_called_once()
    mock_bus.stop.assert_called_once()


# Khala.receive expects a Message object, so we need to wrap the dicts
# This highlights the Khala.receive expecting Message vs dict issue
# For now, we'll mock it to return a Message object whose msg_type and event match the dict
def create_mock_message(event_dict):
    msg = Message(
        channel=event_dict.get("channel"),
        sender=event_dict.get("sender"),
        event=event_dict.get("payload"),
        msg_type=event_dict.get("type"),
        timestamp=event_dict.get("timestamp"),
    )
    # Add content to event if present in event_dict
    if "content" in event_dict:
        msg.event["content"] = event_dict["content"]
    return msg


@pytest.mark.asyncio
async def test_protoss_async_iterator(mock_bus, mock_khala):
    """Protoss yields events as an async iterator."""
    vision = "test vision for iterator"

    # Prepare mock Khala.receive to yield a sequence of events
    event_queue = asyncio.Queue()

    # Simulate agent spawn event
    agent_spawn_event = {
        "type": "agent_spawn",
        "channel": "nexus",
        "sender": "arbiter-123",
        "timestamp": asyncio.get_event_loop().time(),
        "coordination_id": str(uuid.uuid4()),
        "payload": {"agent_id": "arbiter-123", "agent_type": "arbiter"},
    }
    # Simulate an agent message
    agent_message_event = {
        "type": "agent_message",
        "channel": "nexus",
        "sender": "arbiter-123",
        "timestamp": asyncio.get_event_loop().time() + 1,
        "coordination_id": str(uuid.uuid4()),
        "content": "Hello from arbiter!",
        "payload": {"content": "Hello from arbiter!"},
    }
    # Simulate coordination complete event
    coordination_complete_event = {
        "type": "coordination_complete",
        "channel": "nexus",
        "sender": "system",
        "timestamp": asyncio.get_event_loop().time() + 2,
        "coordination_id": str(uuid.uuid4()),
        "payload": {"result": "Success"},
    }

    await event_queue.put(create_mock_message(agent_spawn_event))
    await event_queue.put(create_mock_message(agent_message_event))
    await event_queue.put(create_mock_message(coordination_complete_event))

    mock_khala.receive.side_effect = event_queue.get

    received_events = []
    async with Protoss(vision) as swarm:
        async for event in swarm:
            received_events.append(event)
            if event["type"] == "coordination_complete":
                break  # Stop iteration on completion

    assert len(received_events) == 3
    assert received_events[0]["type"] == "agent_spawn"
    assert received_events[1]["type"] == "agent_message"
    assert received_events[2]["type"] == "coordination_complete"
    assert received_events[1]["content"] == "Hello from arbiter!"
    assert received_events[2]["payload"]["result"] == "Success"


@pytest.mark.asyncio
async def test_protoss_completion(mock_bus, mock_khala):
    """Protoss.completion() awaits coordination completion."""
    vision = "test vision for completion"

    event_queue = asyncio.Queue()
    coordination_complete_event = {
        "type": "coordination_complete",
        "channel": "nexus",
        "sender": "system",
        "timestamp": asyncio.get_event_loop().time(),
        "coordination_id": str(uuid.uuid4()),
        "payload": {"result": "Final Result"},
    }
    await event_queue.put(create_mock_message(coordination_complete_event))
    mock_khala.receive.side_effect = event_queue.get

    async with Protoss(vision) as swarm:
        result = await swarm.completion()

    assert result == "Final Result"


@pytest.mark.asyncio
async def test_protoss_await_syntax(mock_bus, mock_khala):
    """'await swarm' syntax works and returns completion result."""
    vision = "test vision for await"

    event_queue = asyncio.Queue()
    coordination_complete_event = {
        "type": "coordination_complete",
        "channel": "nexus",
        "sender": "system",
        "timestamp": asyncio.get_event_loop().time(),
        "coordination_id": str(uuid.uuid4()),
        "payload": {"result": "Await Success"},
    }
    await event_queue.put(create_mock_message(coordination_complete_event))
    mock_khala.receive.side_effect = event_queue.get

    async with Protoss(vision) as swarm:
        result = await swarm  # Test __await__

    assert result == "Await Success"


@pytest.mark.asyncio
async def test_protoss_timeout(mock_bus, mock_khala):
    """Protoss coordination times out if no completion event."""
    vision = "test vision for timeout"
    timeout = 1  # Short timeout for testing

    # Mock Khala.receive to never yield a completion event
    async def never_complete():
        while True:
            await asyncio.sleep(100)  # Sleep indefinitely

    mock_khala.receive.side_effect = never_complete

    async with Protoss(vision, timeout=timeout) as swarm:
        result = await swarm.completion()

    assert result == "Constitutional coordination timeout"
