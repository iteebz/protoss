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
        patch("protoss.core.khala.Khala.connect", new_callable=AsyncMock),
        patch("protoss.core.khala.Khala.disconnect", new_callable=AsyncMock),
        patch("protoss.core.khala.Khala.send", new_callable=AsyncMock) as khala_send,
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
                khala_send.assert_called_once()
                assert result == "Task completed"

            bus_stop.assert_called_once()


@pytest.mark.asyncio
async def test_cathedral_vision_transmission():
    """Cathedral transmits vision with @arbiter to nexus channel."""
    with (
        patch("protoss.core.bus.Bus.start", new_callable=AsyncMock),
        patch("protoss.core.bus.Bus.stop", new_callable=AsyncMock),
        patch("protoss.core.khala.Khala.connect", new_callable=AsyncMock),
        patch("protoss.core.khala.Khala.disconnect", new_callable=AsyncMock),
        patch("protoss.core.khala.Khala.send", new_callable=AsyncMock) as khala_send,
    ):
        with patch.object(
            Protoss, "_await_completion", new_callable=AsyncMock, return_value="Done"
        ):
            async with Protoss("test vision") as swarm:
                await swarm

                # Should send vision with @arbiter mention to nexus via Khala
                khala_send.assert_called_with(
                    content="test vision @arbiter",
                    channel="nexus",
                    sender="human",
                    msg_type="event",
                )
