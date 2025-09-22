import pytest
import asyncio
import os
import tempfile
import pytest_asyncio
from protoss.core.bus import Bus
from protoss.core.protocols import Mention, Despawn


@pytest_asyncio.fixture  # Use pytest_asyncio.fixture
async def bus_integration_fixture():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_bus_integration.db")
        # Use port=0 to let the OS assign a random available port
        bus = Bus(storage_path=db_path, port=0)
        await bus.start()
        yield bus
        await bus.stop()


@pytest.mark.asyncio
async def test_bus_integration_persists_messages(bus_integration_fixture: Bus):
    bus = bus_integration_fixture
    channel = "test_channel_persist"
    sender = "test_sender"
    content = "This is a test message."
    signals = [Mention(agent_name="test_agent")]
    event = {"content": content}

    await bus.transmit(channel, sender, event=event, signals=signals)

    # Verify in-memory history
    in_memory_history = bus.channels[channel].history
    assert len(in_memory_history) == 1
    assert in_memory_history[0].event["content"] == content

    # Verify persisted history via get_history
    persisted_history = await bus.get_history(channel)
    assert len(persisted_history) == 1
    assert persisted_history[0].event["content"] == content
    assert persisted_history[0].sender == sender
    assert len(persisted_history[0].signals) == 1
    assert isinstance(persisted_history[0].signals[0], Mention)
    assert persisted_history[0].signals[0].agent_name == "test_agent"


@pytest.mark.asyncio
async def test_bus_integration_recovers_history_on_restart():
    db_path = None
    channel = "test_channel_recover"
    sender = "recovery_sender"
    content1 = "First message."
    content2 = "Second message."

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_bus_recovery.db")

        # First Bus instance: send messages and stop
        # Use port=0 for random port assignment
        bus1 = Bus(storage_path=db_path, port=0)
        await bus1.start()
        await bus1.transmit(channel, sender, event={"content": content1})
        await bus1.transmit(
            channel, sender, event={"content": content2}, signals=[Despawn()]
        )
        await bus1.stop()

        # Second Bus instance: start with same storage path and check history
        # Use port=0 for random port assignment
        bus2 = Bus(storage_path=db_path, port=0)
        await bus2.start()

        recovered_history = await bus2.get_history(channel)
        assert len(recovered_history) == 2
        assert recovered_history[0].event["content"] == content1
        assert recovered_history[1].event["content"] == content2
        assert len(recovered_history[1].signals) == 1
        assert isinstance(recovered_history[1].signals[0], Despawn)

        await bus2.stop()


@pytest.mark.asyncio
async def test_bus_integration_history_since_timestamp(bus_integration_fixture: Bus):
    bus = bus_integration_fixture
    channel = "test_channel_since"
    sender = "time_traveler"

    await bus.transmit(channel, sender, event={"content": "Message 1"})
    await asyncio.sleep(0.01)  # Ensure distinct timestamps
    msg2_timestamp = bus.channels[channel].history[-1].timestamp
    await bus.transmit(channel, sender, event={"content": "Message 2"})
    await asyncio.sleep(0.01)
    await bus.transmit(channel, sender, event={"content": "Message 3"})

    # Get history since msg2_timestamp
    history_since = await bus.get_history(channel, since_timestamp=msg2_timestamp)
    assert len(history_since) == 2
    assert history_since[0].event["content"] == "Message 2"
    assert history_since[1].event["content"] == "Message 3"

    # Get history since a future timestamp (should be empty)
    history_future = await bus.get_history(
        channel, since_timestamp=bus.channels[channel].history[-1].timestamp + 1
    )
    assert len(history_future) == 0
