"""Event serialization tests."""

from protoss.core.event import Event


def test_event_to_dict():
    """Verify that the Event dataclass serializes correctly to a dictionary."""
    event = Event(
        type="agent_message",
        channel="alpha",
        sender="zealot",
        payload={"content": "hi"},
        coordination_id="coord-1",
        content="hi",
        signals=[],
    )

    payload = event.to_dict()

    assert payload["type"] == "agent_message"
    assert payload["channel"] == "alpha"
    assert payload["sender"] == "zealot"
    assert payload["payload"]["content"] == "hi"
    assert payload["coordination_id"] == "coord-1"
    assert payload["content"] == "hi"
