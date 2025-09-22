"""Unit tests for Bus."""

import asyncio


def test_bus_routes_messages():
    """Bus routes messages to channels."""
    from protoss.core.bus import Bus

    bus = Bus(enable_storage=False)
    asyncio.run(bus.transmit("test", "agent", "hello"))

    assert "test" in bus.channels
    assert len(bus.channels["test"].history) == 1
    assert bus.channels["test"].history[0].content == "hello"
