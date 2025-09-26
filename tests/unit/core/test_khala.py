"""Khala contract tests."""

import json
from unittest.mock import AsyncMock, patch

import pytest
import websockets

from protoss.core.khala import Khala


@pytest.mark.asyncio
async def test_connect_and_disconnect():
    websocket = AsyncMock()
    with patch(
        "protoss.core.khala.websockets.connect", new=AsyncMock(return_value=websocket)
    ):
        khala = Khala("ws://bus")
        await khala.connect(agent_id="unit-1")

    assert khala._websocket is websocket

    await khala.disconnect()
    websocket.close.assert_awaited_once()
    assert khala._websocket is None


@pytest.mark.asyncio
async def test_send_injects_timestamp(monkeypatch):
    websocket = AsyncMock()
    websocket.state = websockets.protocol.State.OPEN

    with patch(
        "protoss.core.khala.websockets.connect", new=AsyncMock(return_value=websocket)
    ):
        khala = Khala("ws://bus")
        await khala.connect(agent_id="unit-1")

    await khala.send({"type": "agent_message", "content": "hi"})

    assert websocket.send.await_count == 1
    payload = json.loads(websocket.send.await_args.args[0])
    assert payload["content"] == "hi"
    assert "timestamp" in payload


@pytest.mark.asyncio
async def test_receive_parses_message(monkeypatch):
    websocket = AsyncMock()
    websocket.state = websockets.protocol.State.OPEN
    websocket.recv.return_value = json.dumps(
        {
            "type": "agent_message",
            "channel": "alpha",
            "sender": "zealot",
            "timestamp": 123,
            "coordination_id": "coord-1",
            "payload": {"content": "hi"},
            "signals": [],
        }
    )

    with patch(
        "protoss.core.khala.websockets.connect", new=AsyncMock(return_value=websocket)
    ):
        khala = Khala("ws://bus")
        await khala.connect(agent_id="unit-1")

    message = await khala.receive()

    assert message.channel == "alpha"
    assert message.payload["content"] == "hi"


@pytest.mark.asyncio
async def test_listen_yields_messages(mock_websocket_aiter):
    # Simulate multiple messages from the websocket
    mock_messages = [
        json.dumps(
            {
                "type": "msg1",
                "channel": "ch1",
                "sender": "s1",
                "timestamp": 1,
                "payload": {"content": "c1"},
            }
        ),
        json.dumps(
            {
                "type": "msg2",
                "channel": "ch2",
                "sender": "s2",
                "timestamp": 2,
                "payload": {"content": "c2"},
            }
        ),
    ]

    websocket = mock_websocket_aiter(mock_messages)

    with patch(
        "protoss.core.khala.websockets.connect", new=AsyncMock(return_value=websocket)
    ):
        khala = Khala("ws://bus")
        await khala.connect(agent_id="unit-1")

        received_messages = []
        async for message in khala.listen():
            received_messages.append(message)

    assert len(received_messages) == 2
    assert received_messages[0].type == "msg1"
    assert received_messages[1].type == "msg2"
    assert received_messages[0].channel == "ch1"
    assert received_messages[1].channel == "ch2"
