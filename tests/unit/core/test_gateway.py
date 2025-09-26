"""Gateway spawning tests."""

from unittest.mock import AsyncMock, patch

import pytest

from protoss.core import gateway


def test_should_spawn_agent_respects_limits():
    active = {"alpha": {"zealot-1"}}

    assert not gateway.should_spawn_agent("zealot", "alpha", active, max_agents=2)
    assert gateway.should_spawn_agent("archon", "alpha", active, max_agents=2)
    assert not gateway.should_spawn_agent("unknown", "alpha", active)


@pytest.mark.asyncio
async def test_spawn_agent_rejects_unknown_type():
    with pytest.raises(ValueError):
        await gateway.spawn_agent("unknown", "alpha", "ws://bus")


@pytest.mark.asyncio
async def test_spawn_agent_invokes_subprocess():
    with patch(
        "protoss.core.gateway.asyncio.create_subprocess_exec", new_callable=AsyncMock
    ) as create_proc:
        process = AsyncMock()
        process.pid = 42
        create_proc.return_value = process

        pids = await gateway.spawn_agent("zealot", "alpha", "ws://bus")

    assert create_proc.await_count == 1
    assert pids == [42]
