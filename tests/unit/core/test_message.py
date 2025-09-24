"""Event/Message conversions."""

from protoss.core.message import Event, Message


def test_event_to_dict_round_trip():
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
    assert payload["payload"]["content"] == "hi"

    message = Message(
        channel=payload["channel"],
        sender=payload["sender"],
        timestamp=payload["timestamp"],
        signals=[],
        event=payload["payload"],
        msg_type=payload["type"],
        coordination_id=payload["coordination_id"],
    )

    assert message.event["content"] == "hi"
