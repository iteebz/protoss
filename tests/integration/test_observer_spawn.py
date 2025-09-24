"""Observer integration tests for mention-driven spawning."""

import asyncio

import pytest

from protoss.core.coordinator import Coordinator
from protoss.core.message import Event
from protoss.core.nexus import Nexus
from protoss.core.observer import Observer
from protoss.core.protocols import Mention


@pytest.mark.asyncio
async def test_observer_spawns_unit_on_mention():
    nexus = Nexus()
    coordinator = Coordinator(nexus)
    coordinator.get_active_units = lambda channel: set()

    spawn_calls = []

    async def fake_spawn(unit_type, channel, bus_url):
        spawn_calls.append((unit_type, channel, bus_url))

    observer = Observer(
        nexus=nexus,
        coordinator=coordinator,
        bus_url="ws://bus",
        spawn_unit_func=fake_spawn,
        max_units=5,
    )

    await observer.start()

    async def wait_for_unit_spawn():
        async for event in nexus.subscribe(event_type="unit_spawn"):
            return event

    spawn_event_task = asyncio.create_task(wait_for_unit_spawn())
    await asyncio.sleep(0)

    mention_event = Event(
        type="agent_message",
        channel="alpha",
        sender="zealot-1",
        coordination_id="coord-2",
        content="@probe we require assistance",
        signals=[Mention(agent_name="probe")],
    )

    await nexus.publish(mention_event)

    emitted_event = await asyncio.wait_for(spawn_event_task, timeout=1)

    assert spawn_calls == [("probe", "alpha", "ws://bus")]
    assert emitted_event.payload["unit_type"] == "probe"
    assert emitted_event.payload["spawned_by"] == "zealot-1"
    assert emitted_event.coordination_id == "coord-2"

    await observer.stop()
