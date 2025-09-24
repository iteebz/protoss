"""Integration tests for Nexus-driven coordination flows."""

import asyncio

import pytest

from protoss.core.coordinator import Coordinator
from protoss.core.message import Event
from protoss.core.nexus import Nexus


@pytest.mark.asyncio
async def test_coordinator_emits_completion_on_despawn():
    nexus = Nexus()
    coordinator = Coordinator(nexus)
    await coordinator.start()

    async def wait_for_completion():
        async for event in nexus.subscribe():
            if event.type == "coordination_complete":
                return event

    completion_task = asyncio.create_task(wait_for_completion())
    await asyncio.sleep(0)

    spawn = Event(
        type="unit_spawn",
        channel="alpha",
        sender="probe-1",
        coordination_id="coord-1",
        payload={"unit_id": "probe-1"},
    )

    despawn = Event(
        type="unit_despawn",
        channel="alpha",
        sender="probe-1",
        coordination_id="coord-1",
        payload={"unit_id": "probe-1"},
    )

    await nexus.publish(spawn)
    await nexus.publish(despawn)

    completion_event = await asyncio.wait_for(completion_task, timeout=1)
    assert completion_event.coordination_id == "coord-1"
    assert completion_event.channel == "alpha"

    await coordinator.stop()
