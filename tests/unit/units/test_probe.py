"""Probe unit contract tests."""

import asyncio
from unittest.mock import AsyncMock

import pytest

from protoss.units.probe import Probe


@pytest.fixture
def probe(monkeypatch):
    monkeypatch.setattr(
        "protoss.units.unit.get_unit_data",
        lambda unit_type: {"identity": [], "guidelines": [], "tools": []},
    )
    pr = Probe(
        unit_type="probe",
        channel="alpha",
        bus_url="ws://bus",
        coordination_id="coord-1",
    )
    return pr


def test_registry_override(probe):
    assert probe.registry_data == {"identity": [], "guidelines": [], "tools": []}


@pytest.mark.asyncio
async def test_execute_processes_events(event_factory, probe):
    event = event_factory(channel="alpha", sender="tester", content="do")

    async def handle(event_arg):
        probe._running = False

    probe.recv_message = AsyncMock(return_value=event)
    probe._handle_probe_command = AsyncMock(side_effect=handle)

    await probe.execute()

    probe.recv_message.assert_awaited()
    probe._handle_probe_command.assert_awaited_once_with(event)
    assert probe._running is False


@pytest.mark.asyncio
async def test_execute_handles_cancelled_error(probe):
    probe.recv_message = AsyncMock(side_effect=asyncio.CancelledError())

    await probe.execute()

    assert probe._running is False
