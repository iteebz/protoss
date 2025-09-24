"""Clean, simple Protoss tests that verify actual behavior."""

import pytest
from protoss.core.protoss import Protoss


@pytest.mark.asyncio
async def test_protoss_init():
    """Protoss initializes with vision and configuration."""
    vision = "test vision"
    swarm = Protoss(vision, port=9999, timeout=30)

    assert swarm.vision == vision
    assert swarm.port == 9999
    assert swarm.timeout == 30
    assert isinstance(swarm.coordination_id, str)


def test_protoss_vision_required():
    """Protoss requires vision to initialize."""
    with pytest.raises(TypeError):
        Protoss()  # Should fail without vision
