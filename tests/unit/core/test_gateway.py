"""Gateway spawning tests."""

from unittest.mock import AsyncMock, patch

import pytest

from protoss.core import gateway


def test_should_spawn_unit_respects_limits():
    active = {"alpha": {"zealot-1"}}

    assert not gateway.should_spawn_unit("zealot", "alpha", active, max_units=2)
    assert gateway.should_spawn_unit("archon", "alpha", active, max_units=2)
    assert not gateway.should_spawn_unit("unknown", "alpha", active)


@pytest.mark.asyncio
async def test_spawn_unit_rejects_unknown_type():
    with pytest.raises(ValueError):
        await gateway.spawn_unit("unknown", "alpha", "ws://bus")


@pytest.mark.asyncio
async def test_spawn_unit_invokes_subprocess():
    with patch(
        "protoss.core.gateway.asyncio.create_subprocess_exec", new_callable=AsyncMock
    ) as create_proc:
        process = AsyncMock()
        process.pid = 42
        create_proc.return_value = process

        pids = await gateway.spawn_unit("zealot", "alpha", "ws://bus")

    assert create_proc.await_count == 1
    assert pids == [42]
