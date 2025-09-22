"""Message dataclass tests."""

import time
from protoss.core.message import Message
from protoss.core.protocols import Mention, Despawn


def test_message_creation():
    """Message creates with required fields."""
    msg = Message("general", "agent_id")

    assert msg.channel == "general"
    assert msg.sender == "agent_id"
    assert isinstance(msg.timestamp, float)
    assert msg.signals == []
    assert msg.event is None


def test_message_with_event():
    """Message stores event data."""
    event_data = {"content": "test message"}
    msg = Message("channel", "sender", event=event_data)

    assert msg.event == event_data


def test_message_with_signals():
    """Message stores signal objects."""
    signals = [Mention(agent_name="zealot"), Despawn()]
    msg = Message("channel", "sender", signals=signals)

    assert msg.signals == signals


def test_message_timestamp_auto():
    """Message auto-generates timestamp."""
    msg = Message("test", "test")
    assert abs(msg.timestamp - time.time()) < 1


def test_message_equality():
    """Messages with same data are equal."""
    t = time.time()
    msg1 = Message("ch", "s", timestamp=t, event={"c": "v"})
    msg2 = Message("ch", "s", timestamp=t, event={"c": "v"})
    msg3 = Message("ch", "different", timestamp=t, event={"c": "v"})

    assert msg1 == msg2
    assert msg1 != msg3
