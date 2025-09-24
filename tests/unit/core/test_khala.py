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
        await khala.connect(unit_id="unit-1")

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
        await khala.connect(unit_id="unit-1")

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
        await khala.connect(unit_id="unit-1")

    message = await khala.receive()

    assert message.channel == "alpha"
    assert message.event["content"] == "hi"
