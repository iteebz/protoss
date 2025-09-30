"""Tests for Bus coordination primitive."""

import asyncio
import time

import pytest

from src.protoss.core.bus import Bus


@pytest.fixture
def temp_bus(tmp_path):
    """Create isolated Bus instance."""
    return Bus(base_dir=str(tmp_path))


@pytest.mark.asyncio
async def test_send_and_get_history(temp_bus):
    """Messages persist and load correctly."""
    await temp_bus.send("alice", "hello", "test")
    await temp_bus.send("bob", "world", "test")

    history = await temp_bus.get_history("test")
    assert len(history) == 2
    assert history[0]["sender"] == "alice"
    assert history[1]["sender"] == "bob"


@pytest.mark.asyncio
async def test_get_history_with_since(temp_bus):
    """Since parameter filters messages correctly."""
    await temp_bus.send("alice", "first", "test")

    await asyncio.sleep(0.01)
    t_cutoff = time.time()
    await asyncio.sleep(0.01)

    await temp_bus.send("bob", "second", "test")

    history = await temp_bus.get_history("test", since=t_cutoff)
    assert len(history) == 1
    assert history[0]["sender"] == "bob"


@pytest.mark.asyncio
async def test_subscribe_receives_new_messages(temp_bus):
    """Subscribers receive messages in real-time."""
    received = []

    async def subscriber():
        async for msg in temp_bus.subscribe("test"):
            received.append(msg)
            if len(received) == 2:
                break

    sub_task = asyncio.create_task(subscriber())
    await asyncio.sleep(0.01)

    await temp_bus.send("alice", "msg1", "test")
    await temp_bus.send("bob", "msg2", "test")

    await asyncio.wait_for(sub_task, timeout=1.0)

    assert len(received) == 2
    assert received[0].sender == "alice"
    assert received[1].sender == "bob"
