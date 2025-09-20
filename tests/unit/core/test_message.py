"""Message parsing and validation tests."""

from protoss.core.bus import Message


def test_creation():
    """Message creation with required fields."""
    msg = Message("channel", "sender", "content")

    assert msg.channel == "channel"
    assert msg.sender == "sender"
    assert msg.content == "content"
    assert msg.timestamp > 0


def test_mentions():
    """Extract @mentions from content."""
    test_cases = [
        ("Hello @archon", ["archon"]),
        ("@tassadar and @zeratul", ["tassadar", "zeratul"]),
        ("No mentions", []),
        ("@archon @archon", ["archon", "archon"]),  # Don't dedupe
        ("Email test@domain.com", ["domain"]),  # Matches @domain
    ]

    for content, expected in test_cases:
        msg = Message("ch", "sender", content)
        assert msg.mentions == expected


def test_direct_vs_broadcast():
    """Channel prefix determines message routing."""
    # Direct messages (no special prefix)
    direct = Message("agent-123", "sender", "hi")
    assert direct.is_direct_message is True

    # Broadcast messages (special prefixes)
    broadcast_patterns = ["squad-team", "mission-alpha", "channel-general"]
    for pattern in broadcast_patterns:
        broadcast = Message(pattern, "sender", "hi")
        assert broadcast.is_direct_message is False


def test_serialize():
    """Serialize returns content for transmission."""
    msg = Message("ch", "sender", "test content")
    assert msg.serialize() == "test content"


def test_empty_content():
    """Empty content is valid."""
    msg = Message("ch", "sender", "")
    assert msg.content == ""
    assert msg.mentions == []
