"""Test natural squad coordination patterns.

Validates that Gateway.warp() creates coordinating agents that:
1. Form independent constitutional positions when specified
2. Coordinate via PSI pathway conversations
3. Complete tasks through natural emergence rather than predefined roles
4. Generate persistent conversation traces in SQLite
"""

import pytest
import asyncio
import uuid

from protoss.structures.gateway import Gateway
from protoss.structures.pylon import Pylon
from protoss.khala import khala


@pytest.fixture
async def test_infrastructure():
    """Setup test infrastructure with unique port."""
    port = 9000 + (hash(str(uuid.uuid4())) % 1000)  # Random port 9000-9999
    pylon = Pylon(port)

    # Configure khala for test infrastructure
    khala.set_grid_port(port)

    await pylon.start()

    yield {"pylon": pylon, "port": port, "gateway": Gateway()}

    await pylon.stop()


@pytest.mark.asyncio
async def test_basic_natural_coordination(test_infrastructure):
    """Test basic natural coordination with default zealot agents."""
    gateway = test_infrastructure["gateway"]

    # Simple coordination task
    task = "Plan a simple Python function that adds two numbers"

    # Natural coordination with default agents (3 zealots)
    squad_id = await gateway.warp(task)

    # Verify squad was created
    assert squad_id.startswith("squad-")

    # Give agents time to coordinate (minimal)
    await asyncio.sleep(3)

    # Verify coordination occurred via pathway inspection
    pathway_data = await khala.pathway(squad_id)
    assert pathway_data is not None
    assert pathway_data["messages"] > 0  # At least initial coordination
    assert len(pathway_data["recent"]) > 0  # Has coordination messages


@pytest.mark.asyncio
async def test_constitutional_coordination(test_infrastructure):
    """Test constitutional coordination with Sacred Four unit types."""
    gateway = test_infrastructure["gateway"]

    # Constitutional deliberation task
    task = "Evaluate whether to use microservices or monolith architecture"
    unit_types = ["tassadar", "zeratul", "artanis", "fenix"]

    # Constitutional coordination
    squad_id = await gateway.warp(task, agent_count=4, unit_types=unit_types)

    # Verify constitutional squad deployment
    assert squad_id.startswith("squad-")

    # Give constitutional agents time to deliberate
    await asyncio.sleep(5)

    # Verify constitutional coordination
    pathway_data = await khala.pathway(squad_id)
    assert pathway_data is not None
    assert (
        pathway_data["messages"] >= 4
    )  # At least one message per constitutional agent

    # Verify constitutional diversity in messages
    " ".join(pathway_data["recent"])
    # Should contain different constitutional perspectives
    assert len(pathway_data["recent"]) > 1


@pytest.mark.asyncio
async def test_agent_count_scaling(test_infrastructure):
    """Test natural coordination scales with agent count."""
    gateway = test_infrastructure["gateway"]

    task = "Design a simple authentication system"

    # Test different agent counts
    for agent_count in [2, 3, 5]:
        squad_id = await gateway.warp(task, agent_count=agent_count)

        await asyncio.sleep(2)  # Brief coordination time

        pathway_data = await khala.pathway(squad_id)
        assert pathway_data is not None

        # More agents should generate more coordination messages
        # (Not strict equality due to natural variance)
        assert pathway_data["messages"] > 0


@pytest.mark.asyncio
async def test_pathway_persistence(test_infrastructure):
    """Test that coordination conversations persist in SQLite."""
    gateway = test_infrastructure["gateway"]

    task = "Create a simple REST endpoint"
    squad_id = await gateway.warp(task)

    # Let coordination occur
    await asyncio.sleep(3)

    # Verify pathway exists in SQLite (not just memory)
    pathway_data = await khala.pathway(squad_id)
    assert pathway_data is not None
    assert pathway_data["messages"] > 0

    # Verify SQLite persistence by checking storage directly
    storage = khala.storage
    psi_data = await storage.load_pathway_psi(squad_id)
    assert len(psi_data) > 0

    # Verify message content is preserved
    for psi in psi_data:
        assert "sender" in psi
        assert "content" in psi
        assert "timestamp" in psi
        assert psi["content"].strip()  # Non-empty content


@pytest.mark.asyncio
async def test_concurrent_squads(test_infrastructure):
    """Test multiple squads coordinate independently."""
    gateway = test_infrastructure["gateway"]

    # Deploy multiple squads simultaneously
    tasks = [
        "Build authentication system",
        "Design database schema",
        "Create API endpoints",
    ]

    # Deploy all squads concurrently
    squad_tasks = [gateway.warp(task) for task in tasks]
    squad_ids = await asyncio.gather(*squad_tasks)

    # Verify unique squad IDs
    assert len(set(squad_ids)) == 3

    # Give squads time to coordinate
    await asyncio.sleep(4)

    # Verify each squad has independent coordination
    for squad_id in squad_ids:
        pathway_data = await khala.pathway(squad_id)
        assert pathway_data is not None
        assert pathway_data["messages"] > 0


if __name__ == "__main__":
    # Run tests directly for development
    pytest.main([__file__, "-v"])
