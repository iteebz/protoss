"""Bus contract tests."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from protoss.core.bus import Bus
from protoss.core.message import Event
from protoss.core.protocols import Mention


@pytest.mark.asyncio
async def test_transmit_publishes_canonical_event(monkeypatch):
    nexus = AsyncMock()
    bus = Bus(nexus=nexus, port=0)
    bus.storage.save_event = AsyncMock()

    captured_event: Event | None = None

    async def capture(event: Event):
        nonlocal captured_event
        captured_event = event

    nexus.publish.side_effect = capture
    mock_signal = Mention(agent_name="mock")

    monkeypatch.setattr("protoss.core.parser.signals", lambda content: [mock_signal])

    await bus.transmit(
        channel="alpha",
        sender="zealot",
        event_type="agent_message",
        content="Hello",
        coordination_id="coord-9",
        event_payload={"content": "Hello"},
    )

    assert nexus.publish.await_count == 1
    assert captured_event is not None
    assert captured_event.type == "agent_message"
    assert captured_event.channel == "alpha"
    assert captured_event.content == "Hello"
    assert captured_event.coordination_id == "coord-9"
    assert captured_event.payload["content"] == "Hello"
    assert captured_event.signals == [mock_signal]
    bus.storage.save_event.assert_awaited_once()


@pytest.mark.asyncio
async def test_handler_registers_sender_and_routes(monkeypatch):
    nexus = AsyncMock()
    bus = Bus(nexus=nexus, port=0)
    bus.transmit = AsyncMock()

    message = {
        "type": "agent_message",
        "channel": "alpha",
        "content": "Hello",
        "coordination_id": "coord-9",
    }

    class StubWebSocket:
        def __init__(self, messages):
            self.request = type("Request", (), {"path": "/zealot"})()
            self._messages = list(messages)

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self._messages:
                return self._messages.pop(0)
            raise StopAsyncIteration

        async def send(self, payload):  # pragma: no cover - not used in this test
            pass

    websocket = StubWebSocket([json.dumps(message)])

    await bus._handler(websocket)

    assert "zealot" not in bus.connections
    assert bus.channels["alpha"].subscribers == {"zealot"}
    bus.transmit.assert_awaited_once_with(
        channel="alpha",
        sender="zealot",
        event_type="agent_message",
        coordination_id="coord-9",
        content="Hello",
        payload=None,
    )


@pytest.mark.asyncio
async def test_start_uses_websockets_serve():
    nexus = AsyncMock()
    bus = Bus(nexus=nexus, port=0)

    server = MagicMock()
    server.sockets = [
        MagicMock(getsockname=MagicMock(return_value=("127.0.0.1", 9999)))
    ]

    with patch(
        "protoss.core.bus.websockets.serve", new_callable=AsyncMock
    ) as mock_serve:
        mock_serve.return_value = server
        await bus.start()

    mock_serve.assert_awaited_once()
    assert bus.server is server
    assert bus.port == 9999


@pytest.mark.asyncio
async def test_broadcast_skips_sender():
    nexus = AsyncMock()
    bus = Bus(nexus=nexus, port=0)

    sender_socket = AsyncMock()
    peer_socket = AsyncMock()
    bus.connections = {"zealot": sender_socket, "archon": peer_socket}
    bus.register("alpha", "zealot")
    bus.register("alpha", "archon")

    event = Event(
        type="agent_message",
        channel="alpha",
        sender="zealot",
        payload={},
        content="Hi",
        signals=[],
    )

    await bus._broadcast_event(event)

    sender_socket.send.assert_not_called()
    peer_socket.send.assert_called_once()
    payload = json.loads(peer_socket.send.await_args.args[0])
    assert payload["channel"] == "alpha"
    assert payload["sender"] == "zealot"
