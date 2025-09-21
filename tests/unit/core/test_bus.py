"""Bus coordination and routing tests."""

import pytest
from protoss.core.bus import Bus


def test_initialization():
    """Bus starts with clean state."""
    bus = Bus(enable_storage=False)

    assert bus.channels == {}
    assert bus.memories == {}
    assert bus.max_memory == 50
    assert bus.port == 8888
    assert bus.server is None


def test_port_config():
    """Custom port configuration."""
    bus = Bus(port=9999, enable_storage=False)
    assert bus.port == 9999


def test_channel_registration():
    """Register agents to channels."""
    bus = Bus(enable_storage=False)

    bus.register("squad-alpha", "agent-1")
    assert "squad-alpha" in bus.channels
    assert "agent-1" in bus.channels["squad-alpha"]


@pytest.mark.asyncio
async def test_broadcast_routing():
    """Broadcast messages create channels and store memories."""
    bus = Bus(enable_storage=False)

    await bus.transmit("squad-alpha", "agent-1", "test message")

    assert "squad-alpha" in bus.memories
    assert len(bus.memories["squad-alpha"]) == 1
    assert bus.memories["squad-alpha"][0].content == "test message"


@pytest.mark.asyncio
async def test_memory_trimming():
    """Memory trimmed when exceeding max_memory."""
    bus = Bus(max_memory=3, enable_storage=False)

    # Send 5 messages, should keep only last 3
    for i in range(5):
        await bus.transmit("squad-test", "sender", f"msg-{i}")

    memories = bus.memories["squad-test"]
    assert len(memories) == 3

    # Should keep most recent
    contents = [msg.content for msg in memories]
    assert "msg-2" in contents
    assert "msg-3" in contents
    assert "msg-4" in contents
    assert "msg-0" not in contents


@pytest.mark.asyncio
async def test_mention_detection():
    """@mentions are detected and stored in messages."""
    bus = Bus(enable_storage=False)
    await bus.transmit("squad-discuss", "user", "Help @archon and @tassadar")

    message = bus.memories["squad-discuss"][0]
    assert "@archon" in message.content
    assert "@tassadar" in message.content
    assert mentions.extract_mentions(message.content) == ["archon", "tassadar"]


def test_get_history():
    """Retrieve channel message history."""
    bus = Bus(enable_storage=False)

    # Empty channel returns empty list
    assert bus.get_history("nonexistent") == []

    # TODO: Test with actual messages after implementing sync message storage


def test_channel_task_tracking():
    """Channel task tracking stores canonical task statement."""
    bus = Bus(enable_storage=False)

    bus.set_channel_task("squad-alpha", "Implement auth system")
    assert bus.get_channel_task("squad-alpha") == "Implement auth system"

    # Unknown channel returns None
    assert bus.get_channel_task("squad-beta") is None


def test_status():
    """Bus status reporting."""
    bus = Bus(enable_storage=False)

    status = bus.status()
    assert status["channels"] == 0
    assert status["agents"] == 0
    assert status["memories"] == 0
