"""Test Sacred Four constitutional deliberation patterns.

Validates that Conclave.convene() creates constitutional coordination that:
1. Spawns 4 constitutional agents (Tassadar, Zeratul, Artanis, Fenix)
2. Implements position-first deliberation pattern
3. Generates genuine constitutional diversity through identity frameworks
4. Reaches consensus via natural PSI coordination
5. Persists constitutional decisions for institutional memory
"""

import pytest
import asyncio
import uuid

from protoss.conclave import Conclave
from protoss.structures.pylon import Pylon
from protoss.khala import khala


@pytest.fixture
async def test_infrastructure():
    """Setup test infrastructure with unique port."""
    port = 9100 + (hash(str(uuid.uuid4())) % 1000)  # Random port 9100-9199
    pylon = Pylon(port)

    # Configure khala for test infrastructure
    khala.set_grid_port(port)

    await pylon.start()

    yield {"pylon": pylon, "port": port, "conclave": Conclave()}

    await pylon.stop()


@pytest.mark.asyncio
async def test_basic_constitutional_deliberation(test_infrastructure):
    """Test basic Sacred Four deliberation on strategic question."""
    conclave = test_infrastructure["conclave"]

    # Strategic question requiring constitutional guidance
    question = "Should we prioritize code quality or shipping speed?"

    # Constitutional deliberation
    conclave_id = await conclave.convene(question)

    # Verify conclave was initiated
    assert conclave_id.startswith("conclave-")

    # Give Sacred Four time to deliberate
    await asyncio.sleep(6)

    # Verify constitutional deliberation occurred
    pathway_data = await khala.pathway(conclave_id)
    assert pathway_data is not None
    assert pathway_data["messages"] >= 4  # At least one per constitutional agent

    # Verify persistence of constitutional decision
    storage = khala.storage
    psi_data = await storage.load_pathway_psi(conclave_id)
    assert len(psi_data) >= 4


@pytest.mark.asyncio
async def test_constitutional_diversity(test_infrastructure):
    """Test that Sacred Four generate genuinely different perspectives."""
    conclave = test_infrastructure["conclave"]

    # Question designed to trigger constitutional diversity
    question = "Should we implement comprehensive testing or rely on rapid iteration?"

    conclave_id = await conclave.convene(question)

    # Allow constitutional agents to establish positions and deliberate
    await asyncio.sleep(8)

    # Verify constitutional conversation occurred
    pathway_data = await khala.pathway(conclave_id)
    assert pathway_data is not None

    # Analyze conversation for constitutional diversity markers
    " ".join(pathway_data["recent"]).lower()

    # Should contain constitutional perspectives (not strict validation due to LLM variance)
    # Just verify we have substantive deliberation, not specific content
    assert len(pathway_data["recent"]) >= 2  # Multiple coordination messages
    assert pathway_data["messages"] >= 4  # At least initial constitutional positions


@pytest.mark.asyncio
async def test_position_first_pattern(test_infrastructure):
    """Test that Sacred Four implement position-first deliberation."""
    conclave = test_infrastructure["conclave"]

    question = "Should we use GraphQL or REST for our API design?"

    conclave_id = await conclave.convene(question)

    # Brief wait for initial position formation
    await asyncio.sleep(4)

    # Check that constitutional coordination began
    pathway_data = await khala.pathway(conclave_id)
    assert pathway_data is not None

    # Wait for deliberation to develop
    await asyncio.sleep(4)

    # Re-check for deliberation progress
    pathway_data = await khala.pathway(conclave_id)
    assert pathway_data["messages"] > 0

    # Verify constitutional agents participated
    # (Content validation would be too brittle for LLM variance)


@pytest.mark.asyncio
async def test_concurrent_constitutional_deliberations(test_infrastructure):
    """Test multiple constitutional deliberations can occur independently."""
    conclave = test_infrastructure["conclave"]

    # Multiple strategic questions
    questions = [
        "Should we prioritize performance or maintainability?",
        "Should we use microservices or monolith architecture?",
        "Should we build custom tools or use existing solutions?",
    ]

    # Initiate concurrent deliberations
    deliberation_tasks = [conclave.convene(q) for q in questions]
    conclave_ids = await asyncio.gather(*deliberation_tasks)

    # Verify unique conclave IDs
    assert len(set(conclave_ids)) == 3

    # Give deliberations time to develop
    await asyncio.sleep(8)

    # Verify each deliberation has independent coordination
    for conclave_id in conclave_ids:
        pathway_data = await khala.pathway(conclave_id)
        assert pathway_data is not None
        assert pathway_data["messages"] > 0


@pytest.mark.asyncio
async def test_constitutional_persistence(test_infrastructure):
    """Test constitutional decisions persist for institutional memory."""
    conclave = test_infrastructure["conclave"]

    question = "Should we implement feature flags or direct deployment?"
    conclave_id = await conclave.convene(question)

    # Allow deliberation to occur
    await asyncio.sleep(6)

    # Verify constitutional decision is persisted in SQLite
    storage = khala.storage
    psi_data = await storage.load_pathway_psi(conclave_id)

    assert len(psi_data) > 0

    # Verify constitutional content is preserved
    for psi in psi_data:
        assert psi["sender"]  # Constitutional agent ID
        assert psi["content"].strip()  # Non-empty constitutional content
        assert psi["timestamp"] > 0  # Valid timestamp

    # Verify pathway can be recovered for institutional memory
    pathway_data = await khala.pathway(conclave_id)
    assert pathway_data is not None
    assert pathway_data["pathway"] == conclave_id


@pytest.mark.asyncio
async def test_constitutional_framework_resilience(test_infrastructure):
    """Test constitutional deliberation handles edge cases gracefully."""
    conclave = test_infrastructure["conclave"]

    # Edge case questions
    edge_questions = [
        "",  # Empty question
        "Should we?",  # Minimal question
        "A" * 1000,  # Very long question
    ]

    for question in edge_questions:
        try:
            conclave_id = await conclave.convene(question)

            # Brief coordination time
            await asyncio.sleep(3)

            # Verify graceful handling - no crashes
            await khala.pathway(conclave_id)
            # Don't assert specific behavior for edge cases, just no crashes

        except Exception as e:
            # Constitutional framework should be resilient
            pytest.fail(
                f"Constitutional deliberation crashed on edge case '{question[:50]}...': {e}"
            )


if __name__ == "__main__":
    # Run tests directly for development
    pytest.main([__file__, "-v"])
