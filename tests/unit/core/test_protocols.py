"""Tests for core protocols."""

from src.protoss.core.protocols import Message


def test_message_to_dict():
    """Message converts to dict correctly."""
    msg = Message(sender="alice", content="hello", timestamp=123.456, channel="test")

    d = msg.to_dict()
    assert d["sender"] == "alice"
    assert d["content"] == "hello"
    assert d["timestamp"] == 123.456
    assert d["channel"] == "test"
