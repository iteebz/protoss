"""Tests for the SQLite storage layer."""

import asyncio
import time
from pathlib import Path

import pytest

from src.protoss.lib.sqlite import SQLite


@pytest.fixture
def temp_base_dir(tmp_path: Path) -> str:
    """Create a temporary base directory for isolated test runs."""
    return str(tmp_path)


@pytest.mark.asyncio
async def test_save_and_load_messages(temp_base_dir: str):
    """Verify that messages can be saved and loaded correctly."""
    storage = SQLite(base_dir=temp_base_dir)
    channel = "test_channel"
    sender = "test_sender"
    content = "test_content"
    timestamp1 = time.time()

    # 1. Save a message
    await storage.save_message(channel, sender, content, timestamp1)

    # 2. Load messages and verify the saved message is present
    messages = await storage.load_messages(channel)
    assert len(messages) == 1
    assert messages[0]["sender"] == sender
    assert messages[0]["content"] == content
    assert messages[0]["timestamp"] == timestamp1


@pytest.mark.asyncio
async def test_load_messages_with_since(temp_base_dir: str):
    """Verify that the 'since' parameter correctly filters messages."""
    storage = SQLite(base_dir=temp_base_dir)
    channel = "test_channel"
    timestamp1 = time.time()

    # 1. Save the first message
    await storage.save_message(channel, "sender1", "content1", timestamp1)

    # Ensure a different timestamp for the second message
    await asyncio.sleep(0.01)
    timestamp2 = time.time()

    # 2. Save the second message
    await storage.save_message(channel, "sender2", "content2", timestamp2)

    # 3. Load messages since the first timestamp
    messages_since = await storage.load_messages(channel, since=timestamp1)

    # 4. Verify that only the second message is returned
    assert len(messages_since) == 1
    assert messages_since[0]["sender"] == "sender2"
    assert messages_since[0]["timestamp"] == timestamp2

    # 5. Verify loading all messages still works
    all_messages = await storage.load_messages(channel)
    assert len(all_messages) == 2
