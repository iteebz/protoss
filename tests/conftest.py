import asyncio
from collections import deque
from dataclasses import replace
from typing import Any, Deque, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from protoss.core.config import Config
from protoss.core.message import Event, Message


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
def message_factory() -> Any:
    """Factory for canonical Message objects."""

    def _build(**overrides: Any) -> Message:
        base = Message(
            channel="nexus",
            sender="tester",
            timestamp=123.0,
            signals=[],
            event={"content": "hello"},
            msg_type="agent_message",
            coordination_id="coord-1",
        )
        for key, value in overrides.items():
            setattr(base, key, value)
        return base

    return _build


@pytest.fixture
def protoss_components(monkeypatch: pytest.MonkeyPatch) -> Dict[str, Any]:
    """Patch core Protoss dependencies and expose the doubles for assertions."""

    components: Dict[str, Any] = {}

    nexus = AsyncMock()
    nexus.publish = AsyncMock()
    nexus.subscribe = AsyncMock()
    components["nexus"] = nexus
    monkeypatch.setattr("protoss.core.protoss.Nexus", lambda: nexus)

    bus = MagicMock()
    bus.url = "ws://127.0.0.1:9999"
    bus.start = AsyncMock()
    bus.stop = AsyncMock()
    components["bus"] = bus
    monkeypatch.setattr("protoss.core.protoss.Bus", lambda nexus, port: bus)

    coordinator = MagicMock()
    coordinator.start = AsyncMock()
    coordinator.stop = AsyncMock()
    components["coordinator"] = coordinator
    monkeypatch.setattr("protoss.core.protoss.Coordinator", lambda nexus: coordinator)

    archiver = MagicMock()
    archiver.start = AsyncMock()
    archiver.stop = AsyncMock()
    components["archiver"] = archiver
    monkeypatch.setattr("protoss.core.protoss.Archiver", lambda nexus: archiver)

    observer = MagicMock()
    observer.start = AsyncMock()
    observer.stop = AsyncMock()
    components["observer"] = observer
    monkeypatch.setattr(
        "protoss.core.protoss.Observer",
        lambda nexus, coordinator, bus_url, spawn_unit_func: observer,
    )

    gateway_spawn = AsyncMock()
    components["spawn_unit"] = gateway_spawn
    monkeypatch.setattr("protoss.core.protoss.gateway.spawn_unit", gateway_spawn)

    khala = MagicMock()
    khala.connect = AsyncMock()
    khala.disconnect = AsyncMock()
    components["khala"] = khala
    monkeypatch.setattr("protoss.core.protoss.Khala", lambda bus_url: khala)

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
