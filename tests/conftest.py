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


@pytest.fixture
async def agent_test_harness():
    """Test harness for agent lifecycle management with proper cleanup."""

    class AgentTestHarness:
        def __init__(self):
            self.agents = []
            self.tasks = []

        async def spawn_agent(
            self,
            agent_type: str,
            channel: str,
            bus_url: str,
            coordination_id: str,
            timeout: float = 1.0,
        ):
            """Spawn agent with timeout and proper cleanup."""
            from protoss.core.agent import Agent

            agent = Agent(
                agent_type=agent_type,
                channel=channel,
                bus_url=bus_url,
                coordination_id=coordination_id,
            )
            self.agents.append(agent)

            # Run agent with timeout
            task = asyncio.create_task(agent.run())
            self.tasks.append(task)

            return agent, task

        async def shutdown_agent(self, agent, task, timeout: float = 1.0):
            """Shutdown agent gracefully with timeout."""
            await agent.shutdown()
            try:
                await asyncio.wait_for(task, timeout=timeout)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        async def cleanup(self):
            """Clean shutdown of all agents and tasks."""
            # Signal all agents to shutdown
            for agent in self.agents:
                if agent._running:
                    await agent.shutdown()

            # Wait for all tasks to complete or timeout
            if self.tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*self.tasks, return_exceptions=True), timeout=2.0
                    )
                except asyncio.TimeoutError:
                    # Force cancel remaining tasks
                    for task in self.tasks:
                        if not task.done():
                            task.cancel()
                    await asyncio.gather(*self.tasks, return_exceptions=True)

    harness = AgentTestHarness()
    yield harness
    await harness.cleanup()
