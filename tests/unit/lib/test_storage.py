import pytest
import tempfile
import os
import pytest_asyncio

from src.protoss.lib.storage import SQLite


@pytest_asyncio.fixture
async def mock_sqlite():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_store.db")
        storage = SQLite(db_path=db_path)
        await storage._init_db()
        yield storage


@pytest.mark.asyncio
async def test_sqlite_persistence(mock_sqlite: SQLite):
    """Test that events can be saved and loaded from SQLite storage."""
    storage = mock_sqlite
    channel = "test_channel"
    sender = "test_sender"
    content = "Hello from SQLite!"

    # Create event dict directly for storage
    event_data = {
        "type": "agent_message",
        "channel": channel,
        "sender": sender,
        "timestamp": 1234567890.0,
        "payload": {"content": content},
    }
    await storage.save_event(event_data)

    # Load events and verify
    loaded_events = await storage.load_events(channel=channel)
    assert len(loaded_events) == 1

    loaded_event = loaded_events[0]
    assert loaded_event["channel"] == channel
    assert loaded_event["sender"] == sender
    assert loaded_event["payload"]["content"] == content
    assert loaded_event["timestamp"] is not None


@pytest.mark.asyncio
async def test_sqlite_multiple_events(mock_sqlite: SQLite):
    """Test loading events with filters."""
    storage = mock_sqlite

    # Create multiple events
    events = [
        {
            "type": "agent_message",
            "channel": "ch1",
            "sender": "s1",
            "timestamp": 1000.0,
            "payload": {"content": "msg1"},
        },
        {
            "type": "agent_message",
            "channel": "ch1",
            "sender": "s2",
            "timestamp": 2000.0,
            "payload": {"content": "msg2"},
        },
        {
            "type": "agent_message",
            "channel": "ch2",
            "sender": "s3",
            "timestamp": 3000.0,
            "payload": {"content": "msg3"},
        },
    ]

    for event in events:
        await storage.save_event(event)

    # Test channel filtering
    ch1_events = await storage.load_events(channel="ch1")
    assert len(ch1_events) == 2

    # Test timestamp filtering
    recent_events = await storage.load_events(channel="ch1", since=1500.0)
    assert len(recent_events) == 1
    assert recent_events[0]["payload"]["content"] == "msg2"
