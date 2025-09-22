"""Protoss cathedral interface tests."""

import pytest
from unittest.mock import patch, AsyncMock
from protoss.core.protoss import Protoss


def test_protoss_init():
    """Protoss initializes with vision and configuration."""
    swarm = Protoss("test vision", port=9999, max_agents=50)

    assert swarm.vision == "test vision"
    assert swarm.port == 9999
    assert swarm.max_agents == 50
    assert swarm.bus.port == 9999
    assert swarm.bus.max_agents == 50


@pytest.mark.asyncio
async def test_protoss_context_manager():
    """Protoss context manager handles bus lifecycle."""
    from protoss.core.bus import Bus

    with (
        patch.object(Bus, "start", new_callable=AsyncMock) as mock_bus_start,
        patch.object(Bus, "stop", new_callable=AsyncMock) as mock_bus_stop,
    ):
        async with Protoss("test vision"):
            mock_bus_start.assert_called_once()

        mock_bus_stop.assert_called_once()
