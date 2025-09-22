"""Unit tests for Message."""


def test_message_creation():
    """Message creates with timestamp."""
    from protoss.core.message import Message

    msg = Message("channel", "sender", "content")

    assert msg.channel == "channel"
    assert msg.sender == "sender"
    assert msg.content == "content"
    assert msg.timestamp > 0
