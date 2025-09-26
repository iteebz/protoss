import asyncio
from collections import deque
from dataclasses import replace
from typing import Any, Deque, Dict
from unittest.mock import AsyncMock

import pytest
import websockets

from protoss.core.config import Config
from protoss.core.event import Event


@pytest.fixture
def config() -> Config:
    """Canonical config with default settings."""
    return Config()


@pytest.fixture
def event_factory() -> Any:
    """Factory for canonical Event objects."""

    def _build(**overrides: Any) -> Event:
        base = Event(
            type="agent_message",
            channel="nexus",
            sender="tester",
            timestamp=123.0,
            payload={"content": "hello"},
            coordination_id="coord-1",
            content="hello",
            signals=[],
        )
        return replace(base, **overrides)

    return _build


@pytest.fixture
def protoss_components(monkeypatch: pytest.MonkeyPatch) -> Dict[str, Any]:
    """Patch core Protoss dependencies and expose the doubles for assertions."""

    components: Dict[str, Any] = {}

    bus = AsyncMock()
    bus.url = "ws://127.0.0.1:9999"
    bus.start = AsyncMock()
    bus.stop = AsyncMock()
    bus.publish = AsyncMock()
    bus.subscribe = AsyncMock()
    bus.get_events = AsyncMock(return_value=[])
    components["bus"] = bus
    monkeypatch.setattr("protoss.core.protoss.Bus", lambda port: bus)
    monkeypatch.setattr(
        "protoss.core.bus.Bus", lambda port, storage_path, max_units: bus
    )

    khala = AsyncMock()
    khala.connect = AsyncMock()
    khala.disconnect = AsyncMock()
    components["khala"] = khala
    monkeypatch.setattr("protoss.core.protoss.Khala", lambda bus_url: khala)
    monkeypatch.setattr("protoss.core.khala.Khala", lambda bus_url: khala)

    gateway_spawn = AsyncMock()
    components["spawn_agent"] = gateway_spawn
    monkeypatch.setattr("protoss.core.bus.gateway.spawn_agent", gateway_spawn)

    return components


class AsyncQueue:
    """Simple async queue backed by deque for deterministic tests."""

    def __init__(self):
        self._queue: Deque[Any] = deque()

    def push(self, item: Any) -> None:
        self._queue.append(item)

    async def __aiter__(self):  # pragma: no cover - helper for tests needing streams
        while self._queue:
            yield self._queue.popleft()
            await asyncio.sleep(0)


@pytest.fixture
def async_queue() -> AsyncQueue:
    return AsyncQueue()


@pytest.fixture
def mock_websocket_aiter():
    """Fixture to create a mock websocket that behaves as an async iterator."""

    class AsyncIteratorMock:
        def __init__(self, messages):
            self._messages = iter(messages)

        async def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self._messages)
            except StopIteration:
                raise StopAsyncIteration

    def _factory(messages):
        websocket = AsyncMock()
        websocket.state = websockets.protocol.State.OPEN
        # Fix: properly handle self parameter in lambda
        async_iter = AsyncIteratorMock(messages)
        websocket.__aiter__ = lambda self: async_iter
        return websocket

    return _factory
