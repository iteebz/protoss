"""Unit base class tests."""

from unittest.mock import AsyncMock, patch

import pytest
import websockets

from protoss.units.unit import Unit


@pytest.fixture
def unit(monkeypatch):
    monkeypatch.setattr(
        "protoss.units.unit.get_unit_data",
        lambda unit_type: {
            "identity": ["I am a test unit."],
            "guidelines": [],
            "tools": [],
        },
    )

    u = Unit(
        unit_type="zealot",
        channel="alpha",
        bus_url="ws://bus",
        coordination_id="coord-1",
    )
    khala = AsyncMock()
    khala._websocket = AsyncMock()
    khala._websocket.state = websockets.protocol.State.OPEN
    u.khala = khala
    return u


def test_initialization_loads_registry(unit):
    assert unit.unit_type == "zealot"
    assert unit.registry_data["identity"] == ["I am a test unit."]
    assert unit.bus_url == "ws://bus"


@pytest.mark.asyncio
async def test_message_to_event(unit, message_factory):
    event = unit._message_to_event(message_factory())
    assert event.channel == "nexus"
    assert event.payload["content"] == "hello"


@pytest.mark.asyncio
async def test_send_message_uses_khala(unit):
    with patch("protoss.units.unit.parser.signals", return_value=[]):
        await unit.send_message("hi", "agent_message")

    assert unit.khala.send.await_count == 1
    payload = unit.khala.send.await_args.args[0]
    assert payload["content"] == "hi"
    assert payload["channel"] == "alpha"


@pytest.mark.asyncio
async def test_recv_message_returns_event(unit, message_factory):
    unit.khala.receive.return_value = message_factory()
    event = await unit.recv_message()
    assert event.content == "hello"


@pytest.mark.asyncio
async def test_run_handles_lifecycle(monkeypatch):
    monkeypatch.setattr(
        "protoss.units.unit.get_unit_data",
        lambda unit_type: {"identity": [], "guidelines": [], "tools": []},
    )

    unit = Unit(
        unit_type="zealot",
        channel="alpha",
        bus_url="ws://bus",
        coordination_id="coord-1",
    )

    unit._connect_websocket = AsyncMock()
    unit.send_message = AsyncMock()
    unit.execute = AsyncMock()
    unit.khala = AsyncMock()

    await unit.run()

    unit._connect_websocket.assert_awaited_once()
    unit.execute.assert_awaited_once()

    unit.send_message.assert_any_await(
        content=f"Unit {unit.unit_id} ({unit.unit_type}) spawned.",
        event_type="unit_spawn",
        event_payload={"unit_id": unit.unit_id, "unit_type": unit.unit_type},
    )
    unit.send_message.assert_any_await(
        content=f"Unit {unit.unit_id} ({unit.unit_type}) despawned.",
        event_type="unit_despawn",
        event_payload={"unit_id": unit.unit_id, "unit_type": unit.unit_type},
    )
    unit.khala.disconnect.assert_awaited_once()
