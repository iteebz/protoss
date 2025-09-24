"""Observer tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from protoss.core.observer import Observer
from protoss.core.protocols import Mention


@pytest.mark.asyncio
async def test_handle_unit_message_spawns_and_publishes(event_factory):
    nexus = MagicMock()
    nexus.publish = AsyncMock()
    coordinator = MagicMock()
    coordinator.get_active_units.return_value = set()
    spawn = AsyncMock()

    observer = Observer(
        nexus=nexus,
        coordinator=coordinator,
        bus_url="ws://bus",
        spawn_unit_func=spawn,
        max_units=10,
    )

    event = event_factory(
        signals=[Mention(agent_name="zealot")],
        channel="alpha",
        sender="probe",
    )

    with patch("protoss.core.gateway.should_spawn_unit", return_value=True):
        await observer._handle_unit_message(event)

    spawn.assert_awaited_once_with("zealot", "alpha", "ws://bus")
    nexus.publish.assert_awaited()


@pytest.mark.asyncio
async def test_handle_unit_message_skips_without_mentions(event_factory):
    nexus = MagicMock()
    nexus.publish = AsyncMock()
    coordinator = MagicMock()
    spawn = AsyncMock()

    observer = Observer(
        nexus=nexus,
        coordinator=coordinator,
        bus_url="ws://bus",
        spawn_unit_func=spawn,
        max_units=10,
    )

    await observer._handle_unit_message(event_factory(signals=[]))

    spawn.assert_not_called()
    nexus.publish.assert_not_called()
