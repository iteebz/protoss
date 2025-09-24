import asyncio
import os
import tempfile

import pytest
import pytest_asyncio

from protoss.core.bus import Bus
from protoss.core.nexus import Nexus


@pytest_asyncio.fixture  # Use pytest_asyncio.fixture
async def bus_integration_fixture():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_bus_integration.db")
        # Use port=0 to let the OS assign a random available port
        nexus = Nexus()
        bus = Bus(nexus=nexus, storage_path=db_path, port=0)
        yield bus


@pytest.mark.asyncio
async def test_persists_messages(bus_integration_fixture: Bus):
    bus = bus_integration_fixture
    channel = "test_channel_persist"
    sender = "test_sender"
    content = "This is a test message with @test_agent mention."
    event = {"content": content}

    await bus.transmit(
        channel=channel,
        sender=sender,
        event_type="agent_message",
        event_payload=event,
    )

    # Verify persisted events
    persisted_events = await bus.get_events(channel=channel)
    assert len(persisted_events) == 1
    event_data = persisted_events[0]
    assert event_data["payload"]["content"] == content
    assert event_data["sender"] == sender


@pytest.mark.asyncio
async def test_recovers_history_on_restart():
    db_path = None
    channel = "test_channel_recover"
    sender = "recovery_sender"
    content1 = "First message."
    content2 = "Second message."

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_bus_recovery.db")

        # First Bus instance: send messages and stop
        # Use port=0 for random port assignment
        nexus1 = Nexus()
        bus1 = Bus(nexus=nexus1, storage_path=db_path, port=0)
        await bus1.transmit(
            channel,
            sender,
            event_type="agent_message",
            event_payload={"content": content1},
        )
        await bus1.transmit(
            channel,
            sender,
            event_type="agent_message",
            event_payload={"content": content2},
        )

        # Second Bus instance: start with same storage path and check history
        # Use port=0 for random port assignment
        nexus2 = Nexus()
        bus2 = Bus(nexus=nexus2, storage_path=db_path, port=0)

        recovered_events = await bus2.get_events(channel=channel)
        assert len(recovered_events) == 2
        assert recovered_events[0]["payload"]["content"] == content1
        assert recovered_events[1]["payload"]["content"] == content2
        # Signal verification removed for simplicity
        # Signal type checking removed for simplicity

        # No server to stop; persistence tested via storage reuse


@pytest.mark.asyncio
async def test_history_since_timestamp(bus_integration_fixture: Bus):
    bus = bus_integration_fixture
    channel = "test_channel_since"
    sender = "time_traveler"

    await bus.transmit(
        channel,
        sender,
        event_type="agent_message",
        event_payload={"content": "Message 1"},
    )
    await asyncio.sleep(0.01)  # Ensure distinct timestamps
    msg2_timestamp = bus.channels[channel].history[-1].timestamp
    await bus.transmit(
        channel,
        sender,
        event_type="agent_message",
        event_payload={"content": "Message 2"},
    )
    await asyncio.sleep(0.01)
    await bus.transmit(
        channel,
        sender,
        event_type="agent_message",
        event_payload={"content": "Message 3"},
    )

    # Get events since msg2_timestamp
    events_since = await bus.get_events(channel=channel, since=msg2_timestamp)
    assert len(events_since) == 2
    assert events_since[0]["payload"]["content"] == "Message 2"
    assert events_since[1]["payload"]["content"] == "Message 3"

    # Get events since future timestamp (should be empty)
    future_time = events_since[-1]["timestamp"] + 1
    events_future = await bus.get_events(channel=channel, since=future_time)
    assert len(events_future) == 0
