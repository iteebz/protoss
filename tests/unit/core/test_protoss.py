"""Protoss orchestration tests."""

import pytest

from protoss.core.protoss import Protoss


@pytest.mark.asyncio
async def test_context_manager_starts_and_stops(protoss_components):
    async with Protoss("Build the cathedral"):
        pass

    bus = protoss_components["bus"]
    coordinator = protoss_components["coordinator"]
    archiver = protoss_components["archiver"]
    observer = protoss_components["observer"]
    khala = protoss_components["khala"]

    bus.start.assert_awaited_once()
    coordinator.start.assert_awaited_once()
    archiver.start.assert_awaited_once()
    observer.start.assert_awaited_once()
    khala.connect.assert_awaited_once_with(unit_id="protoss_coordinator")

    observer.stop.assert_awaited_once()
    archiver.stop.assert_awaited_once()
    coordinator.stop.assert_awaited_once()
    bus.stop.assert_awaited_once()
    khala.disconnect.assert_awaited_once()


def test_generates_unique_coordination_id():
    p1 = Protoss("vision")
    p2 = Protoss("vision")

    assert p1.coordination_id != p2.coordination_id
    assert p1.coordination_id
