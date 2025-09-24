"""Coordinator contract tests."""

from unittest.mock import AsyncMock

import pytest

from protoss.core.coordinator import Coordinator
from protoss.core.message import Event


@pytest.mark.asyncio
async def test_handle_event_tracks_spawn(event_factory):
    nexus = AsyncMock()
    coordinator = Coordinator(nexus)

    spawn = event_factory(
        type="unit_spawn",
        channel="alpha",
        coordination_id="coord-1",
        payload={"unit_type": "zealot", "unit_id": "zealot-1"},
    )

    await coordinator._handle_event(spawn)

    coordination = coordinator.coordinations["coord-1"]
    assert coordination.status == "active"
    assert coordination.had_units is True
    assert coordination.channels["alpha"] == {"zealot-1"}


@pytest.mark.asyncio
async def test_schedule_completion_emits_completion(monkeypatch):
    published = []

    async def capture(event: Event):
        published.append(event)

    nexus = AsyncMock()
    nexus.publish.side_effect = capture
    coordinator = Coordinator(nexus)

    class StubCoordination:
        def __init__(self):
            self.status = "active"
            self.had_units = True
            self.channels = {"alpha": set()}
            self.pending_completion_task = None

        def is_empty(self) -> bool:
            return True

    coordinator.coordinations["coord-1"] = StubCoordination()

    await coordinator._schedule_completion_emit("coord-1", "alpha")

    assert published
    completion = published[0]
    assert completion.type == "coordination_complete"
    assert completion.channel == "alpha"
    assert completion.coordination_id == "coord-1"


def test_get_active_units_ignores_completed():
    nexus = AsyncMock()
    coordinator = Coordinator(nexus)

    class ActiveCoord:
        status = "active"
        channels = {"alpha": {"zealot-1"}}

    class DoneCoord:
        status = "complete"
        channels = {"alpha": {"archon-1"}}

    coordinator.coordinations = {"a": ActiveCoord(), "d": DoneCoord()}

    assert coordinator.get_active_units("alpha") == {"zealot-1"}
    assert coordinator.get_active_units("beta") == set()
