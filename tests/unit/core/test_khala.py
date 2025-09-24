import pytest
from unittest.mock import AsyncMock, patch
import asyncio
import json

from protoss.core.khala import Khala
import websockets  # Import websockets for State.OPEN


@pytest.fixture
def mock_websocket_connection():
    """Mocks a websockets.WebSocketClientProtocol connection."""
    mock = AsyncMock()
    mock.state = websockets.protocol.State.OPEN
    mock.send = AsyncMock()
    mock.recv = AsyncMock()  # For Khala.receive
    return mock


@pytest.mark.asyncio
async def test_khala_connect_disconnect(mock_websocket_connection):
    """Khala connects and disconnects properly."""
    with patch("websockets.connect", AsyncMock(return_value=mock_websocket_connection)):
        khala = Khala(bus_url="ws://localhost:8888")
        await khala.connect(client_id="test_client")
        mock_websocket_connection.send.assert_not_called()  # No message sent on connect
        assert khala._websocket is not None

        await khala.disconnect()
        mock_websocket_connection.close.assert_called_once()
        assert khala._websocket is None


@pytest.mark.asyncio
async def test_khala_send_structured_event(mock_websocket_connection):
    """Khala sends structured events correctly."""
    with patch("websockets.connect", AsyncMock(return_value=mock_websocket_connection)):
        khala = Khala(bus_url="ws://localhost:8888")
        await khala.connect(client_id="test_client")

        event = {
            "type": "agent_message",
            "channel": "nexus",
            "sender": "test_client",
            "coordination_id": "test-coord-1",
            "content": "Hello from Khala!",
            "payload": {"key": "value"},
            "signals": [{"type": "mention", "agent_name": "arbiter"}],
        }
        await khala.send(event)

        mock_websocket_connection.send.assert_called_once()
        sent_payload = json.loads(mock_websocket_connection.send.call_args[0][0])

        assert sent_payload["type"] == event["type"]
        assert sent_payload["channel"] == event["channel"]
        assert sent_payload["sender"] == event["sender"]
        assert sent_payload["coordination_id"] == event["coordination_id"]
        assert sent_payload["content"] == event["content"]
        assert sent_payload["payload"] == event["payload"]
        assert sent_payload["signals"][0]["type"] == "mention"


@pytest.mark.asyncio
async def test_khala_receive_structured_event(mock_websocket_connection):
    """Khala receives and parses structured events correctly."""
    with patch("websockets.connect", AsyncMock(return_value=mock_websocket_connection)):
        khala = Khala(bus_url="ws://localhost:8888")
        await khala.connect(client_id="test_client")

        received_event_dict = {
            "type": "agent_message",
            "channel": "nexus",
            "sender": "arbiter-1",
            "coordination_id": "test-coord-1",
            "content": "Response from Arbiter",
            "payload": {"response": "ok"},
            "timestamp": asyncio.get_event_loop().time(),
            "signals": [],
        }
        mock_websocket_connection.recv.return_value = json.dumps(received_event_dict)

        event = await khala.receive()

        assert event.msg_type == received_event_dict["type"]
        assert event.channel == received_event_dict["channel"]
        assert event.sender == received_event_dict["sender"]
        assert event.coordination_id == received_event_dict["coordination_id"]
        assert event.event["response"] == received_event_dict["payload"]["response"]
        assert event.event.get("content") == received_event_dict["content"]


@pytest.mark.asyncio
async def test_khala_listen_structured_events(mock_websocket_connection):
    """Khala listens and yields structured events."""
    with patch("websockets.connect", AsyncMock(return_value=mock_websocket_connection)):
        khala = Khala(bus_url="ws://localhost:8888")
        await khala.connect(client_id="test_client")

        event1_dict = {
            "type": "agent_message",
            "channel": "test_channel",
            "sender": "sender1",
            "timestamp": 1.0,
            "coordination_id": "coord1",
            "payload": {"content": "data1", "key": "value1"},
            "signals": [],
        }
        event2_dict = {
            "type": "agent_message",
            "channel": "test_channel",
            "sender": "sender2",
            "timestamp": 2.0,
            "coordination_id": "coord2",
            "payload": {"content": "data2", "key": "value2"},
            "signals": [],
        }

        # A simpler way to mock the async iterator
        messages_to_receive = [
            json.dumps(event1_dict),
            json.dumps(event2_dict),
        ]

        # Define a proper async iterator for the mock
        class AsyncIterator:
            def __init__(self, seq):
                self.seq = seq
                self.i = 0

            async def __anext__(self):
                if self.i >= len(self.seq):
                    raise StopAsyncIteration
                val = self.seq[self.i]
                self.i += 1
                return val

            def __aiter__(self):
                return self

        def get_async_iterator(*args, **kwargs):
            return AsyncIterator(messages_to_receive)

        mock_websocket_connection.__aiter__ = get_async_iterator
        received_events = []
        async for event in khala.listen():
            received_events.append(event)

        assert len(received_events) == 2
        assert received_events[0].event["content"] == event1_dict["payload"]["content"]
        assert received_events[1].event["content"] == event2_dict["payload"]["content"]
