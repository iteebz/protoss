"""Cathedral interface integration tests."""

import pytest
from unittest.mock import patch, AsyncMock
from protoss.core.protoss import Protoss


@pytest.mark.asyncio
async def test_cathedral_interface():
    """Cathedral interface: async with Protoss(vision) as swarm: result = await swarm"""
    with (
        patch("protoss.core.bus.Bus.start", new_callable=AsyncMock) as bus_start,
        patch("protoss.core.bus.Bus.stop", new_callable=AsyncMock) as bus_stop,
        patch("protoss.core.bus.Bus.transmit", new_callable=AsyncMock) as bus_transmit,
    ):
        # Mock completion detection
        with patch.object(
            Protoss,
            "_await_completion",
            new_callable=AsyncMock,
            return_value="Task completed",
        ):
            async with Protoss("build auth system") as swarm:
                result = await swarm

                bus_start.assert_called_once()
                bus_transmit.assert_called_once()
                assert result == "Task completed"

            bus_stop.assert_called_once()


@pytest.mark.asyncio
async def test_cathedral_vision_transmission():
    """Cathedral transmits vision with @arbiter to nexus channel."""
    with (
        patch("protoss.core.bus.Bus.start", new_callable=AsyncMock),
        patch("protoss.core.bus.Bus.stop", new_callable=AsyncMock),
        patch("protoss.core.bus.Bus.transmit", new_callable=AsyncMock) as transmit,
    ):
        with patch.object(
            Protoss, "_await_completion", new_callable=AsyncMock, return_value="Done"
        ):
            async with Protoss("test vision") as swarm:
                await swarm

                # Should transmit vision with @arbiter mention to nexus
                transmit.assert_called_with(
                    "nexus", "human", event={"content": "test vision @arbiter"}
                )
