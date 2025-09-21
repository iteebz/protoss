
import pytest
from protoss.core.bus import Bus, Channel
from protoss.core.message import Message

@pytest.fixture
def bus():
    """Provides a clean Bus instance for each test."""
    return Bus(max_history=3)

def test_ensure_channel_creation(bus: Bus):
    """Verify that accessing a channel implicitly creates it."""
    assert "channel-1" not in bus.channels
    bus._ensure_channel("channel-1")
    assert "channel-1" in bus.channels
    assert isinstance(bus.channels["channel-1"], Channel)

def test_register_subscriber(bus: Bus):
    """Test that an agent can be registered to a channel."""
    bus.register("channel-1", "zealot-1")
    assert "zealot-1" in bus.channels["channel-1"].subscribers

def test_deregister_subscriber(bus: Bus):
    """Test that an agent can be deregistered from a channel."""
    bus.register("channel-1", "zealot-1")
    bus.register("channel-1", "archon-1")
    assert "zealot-1" in bus.channels["channel-1"].subscribers

    bus.deregister("zealot-1")
    assert "zealot-1" not in bus.channels["channel-1"].subscribers
    assert "archon-1" in bus.channels["channel-1"].subscribers

def test_append_to_history(bus: Bus):
    """Test that messages are appended to the correct channel's history."""
    msg1 = Message("channel-1", "zealot-1", "For Aiur!")
    bus._ensure_channel("channel-1") # Ensure channel exists before appending
    bus._append_to_history(msg1)
    assert len(bus.channels["channel-1"].history) == 1
    assert bus.channels["channel-1"].history[0] == msg1

    msg2 = Message("channel-2", "archon-1", "We are one.")
    bus._ensure_channel("channel-2") # Ensure channel exists before appending
    bus._append_to_history(msg2)
    assert len(bus.channels["channel-1"].history) == 1
    assert len(bus.channels["channel-2"].history) == 1

def test_history_max_limit(bus: Bus):
    """Test that channel history correctly respects the max_history limit."""
    bus._ensure_channel("channel-1")
    
    msg1 = Message("channel-1", "zealot-1", "1")
    msg2 = Message("channel-1", "zealot-1", "2")
    msg3 = Message("channel-1", "zealot-1", "3")
    msg4 = Message("channel-1", "zealot-1", "4")

    bus._append_to_history(msg1)
    bus._append_to_history(msg2)
    bus._append_to_history(msg3)
    
    assert len(bus.channels["channel-1"].history) == 3
    assert bus.channels["channel-1"].history[0].content == "1"

    bus._append_to_history(msg4)

    assert len(bus.channels["channel-1"].history) == 3
    assert bus.channels["channel-1"].history[0].content == "2"
    assert bus.channels["channel-1"].history[2].content == "4"

