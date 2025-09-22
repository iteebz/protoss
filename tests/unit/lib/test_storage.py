import pytest
import asyncio
import os
import tempfile
import pytest_asyncio  # Import pytest_asyncio

from src.protoss.lib.storage import SQLite
from src.protoss.core.message import Message
from src.protoss.core.protocols import Mention, Despawn


@pytest_asyncio.fixture  # Use pytest_asyncio.fixture
async def mock_sqlite():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_store.db")
        storage = SQLite(db_path=db_path)
        await storage._init_db()  # Ensure DB is initialized before tests
        yield storage


@pytest.mark.asyncio
async def test_sqlite_persistence(mock_sqlite: SQLite):
    storage = mock_sqlite
    channel = "test_channel_1"
    sender = "test_sender_1"
    content = "Hello from SQLite!"
    signals = [Mention(agent_name="test_agent"), Despawn()]
    event = {"content": content}

    message = Message(channel=channel, sender=sender, event=event, signals=signals)
    await storage.save_message(message)

    loaded_messages = await storage.load_messages(channel)
    assert len(loaded_messages) == 1
    loaded_message = loaded_messages[0]

    assert loaded_message.channel == channel
    assert loaded_message.sender == sender
    assert loaded_message.event["content"] == content
    assert loaded_message.timestamp is not None
    assert len(loaded_message.signals) == 2
    assert any(isinstance(s, Mention) for s in loaded_message.signals)
    assert any(isinstance(s, Despawn) for s in loaded_message.signals)


@pytest.mark.asyncio
async def test_sqlite_load_channels(mock_sqlite: SQLite):
    storage = mock_sqlite
    channel1 = "channel_a"
    channel2 = "channel_b"

    msg1 = Message(channel=channel1, sender="s1", event={"content": "c1"})
    msg2 = Message(channel=channel1, sender="s2", event={"content": "c2"})
    msg3 = Message(channel=channel2, sender="s3", event={"content": "c3"})

    await storage.save_message(msg1)
    await asyncio.sleep(0.01)  # Ensure timestamps differ
    await storage.save_message(msg2)
    await asyncio.sleep(0.01)
    await storage.save_message(msg3)

    channels_data = await storage.load_channels()
    assert len(channels_data) == 2

    channel_a_data = next(c for c in channels_data if c["name"] == channel1)
    assert channel_a_data["message_count"] == 2
    assert channel_a_data["created_at"] == msg1.timestamp
    assert channel_a_data["last_active"] == msg2.timestamp

    channel_b_data = next(c for c in channels_data if c["name"] == channel2)
    assert channel_b_data["message_count"] == 1
    assert channel_b_data["created_at"] == msg3.timestamp
    assert channel_b_data["last_active"] == msg3.timestamp


@pytest.mark.asyncio
async def test_sqlite_recent(mock_sqlite: SQLite):
    storage = mock_sqlite
    channel = "test_channel_recent"

    for i in range(5):
        msg = Message(
            channel=channel, sender=f"s{i}", event={"content": f"content_{i}"}
        )
        await storage.save_message(msg)
        await asyncio.sleep(0.001)  # Ensure timestamps differ

    recent_contents = await storage.recent(channel, limit=3)
    assert len(recent_contents) == 3
    assert recent_contents == ["content_2", "content_3", "content_4"]

    recent_contents_all = await storage.recent(channel, limit=10)
    assert len(recent_contents_all) == 5
    assert recent_contents_all == [
        "content_0",
        "content_1",
        "content_2",
        "content_3",
        "content_4",
    ]
