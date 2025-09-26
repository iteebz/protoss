"""Protoss orchestration tests."""

import pytest

from protoss.core.protoss import Protoss


@pytest.mark.asyncio
async def test_context_manager_starts_and_stops(protoss_components):
    async with Protoss("Build the cathedral"):
        pass

    bus = protoss_components["bus"]
    khala = protoss_components["khala"]

    bus.start.assert_awaited_once()
    khala.connect.assert_awaited_once_with(agent_id="protoss_client")

    bus.stop.assert_awaited_once()
    khala.disconnect.assert_awaited_once()


def test_generates_unique_coordination_id():
    p1 = Protoss("vision")
    p2 = Protoss("vision")

    assert p1.coordination_id != p2.coordination_id
    assert p1.coordination_id
