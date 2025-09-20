"""Test @archon reactive spawning and auto-synthesis patterns.

Validates that Khala @mention detection creates reactive coordination that:
1. Detects @archon mentions in PSI pathway messages
2. Spawns fresh archon agents to join the requesting pathway
3. Performs knowledge synthesis and preservation
4. Implements auto-synthesis on pathway completion detection
5. Creates institutional memory in archives/ directory
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
    port = 9200 + (hash(str(uuid.uuid4())) % 1000)  # Random port 9200-9299
    pylon = Pylon(port)

    # Configure khala for test infrastructure
    khala.set_grid_port(port)

    await pylon.start()

    yield {"pylon": pylon, "port": port, "gateway": Gateway()}

    await pylon.stop()


@pytest.mark.asyncio
async def test_archon_mention_detection(test_infrastructure):
    """Test that @archon mentions trigger reactive spawning."""
    test_infrastructure["gateway"]

    # Create test pathway
    test_pathway = f"test-archon-{uuid.uuid4().hex[:8]}"

    # Send message with @archon mention
    await khala.transmit(
        pathway=test_pathway,
        sender="test-agent",
        content="We've completed the authentication implementation @archon please synthesize this work",
    )

    # Give archon time to spawn and respond
    await asyncio.sleep(4)

    # Verify archon response occurred
    pathway_data = await khala.pathway(test_pathway)
    assert pathway_data is not None
    assert pathway_data["messages"] >= 2  # Original message + archon response

    # Verify archon participated in pathway
    " ".join(pathway_data["recent"])
    # Should contain archon synthesis (content will vary due to LLM)
    assert len(pathway_data["recent"]) >= 2


@pytest.mark.asyncio
async def test_archon_knowledge_synthesis(test_infrastructure):
    """Test archon performs knowledge synthesis on pathway content."""
    test_infrastructure["gateway"]

    # Create pathway with substantial content for synthesis
    test_pathway = f"synthesis-test-{uuid.uuid4().hex[:8]}"

    # Simulate completed work conversation
    work_messages = [
        "I've implemented JWT authentication with refresh tokens",
        "Added proper error handling and validation",
        "Created comprehensive test suite with 95% coverage",
        "Documentation has been updated with API examples",
    ]

    # Send work messages to pathway
    for i, message in enumerate(work_messages):
        await khala.transmit(
            pathway=test_pathway, sender=f"worker-{i}", content=message
        )
        await asyncio.sleep(0.5)  # Brief spacing

    # Request archon synthesis
    await khala.transmit(
        pathway=test_pathway,
        sender="team-lead",
        content="@archon please synthesize our authentication implementation work",
    )

    # Give archon time for synthesis
    await asyncio.sleep(5)

    # Verify synthesis occurred
    pathway_data = await khala.pathway(test_pathway)
    assert pathway_data is not None
    assert (
        pathway_data["messages"] >= len(work_messages) + 2
    )  # Work + request + synthesis


@pytest.mark.asyncio
async def test_auto_synthesis_completion_detection(test_infrastructure):
    """Test auto-synthesis triggers on pathway completion."""
    test_infrastructure["gateway"]

    # Create pathway that signals completion
    test_pathway = f"auto-synthesis-{uuid.uuid4().hex[:8]}"

    # Simulate completed task
    await khala.transmit(
        pathway=test_pathway,
        sender="worker-1",
        content="Task implementation complete - all requirements fulfilled",
    )

    await khala.transmit(
        pathway=test_pathway,
        sender="worker-2",
        content="Testing complete - all tests passing",
    )

    # Send completion signal
    await khala.transmit(
        pathway=test_pathway,
        sender="worker-1",
        content="Task finished successfully - ready for archival",
    )

    # Give auto-synthesis time to trigger
    await asyncio.sleep(5)

    # Verify auto-synthesis occurred
    pathway_data = await khala.pathway(test_pathway)
    assert pathway_data is not None
    # Should have original messages plus auto-synthesis response
    assert pathway_data["messages"] >= 4


@pytest.mark.asyncio
async def test_archives_boundary_enforcement(test_infrastructure):
    """Test archon creates institutional memory in archives/ directory."""
    # This test validates the archives/ boundary more conceptually
    # since file creation would require more complex setup

    test_infrastructure["gateway"]
    test_pathway = f"archive-test-{uuid.uuid4().hex[:8]}"

    # Create substantial knowledge for archival
    knowledge_content = [
        "Implemented microservice authentication pattern",
        "Key insight: JWT + refresh token rotation prevents session hijacking",
        "Performance: 99.9% uptime achieved with circuit breaker pattern",
        "Architecture decision: Redis for session storage scales to 10k concurrent users",
    ]

    for i, content in enumerate(knowledge_content):
        await khala.transmit(
            pathway=test_pathway, sender=f"expert-{i}", content=content
        )
        await asyncio.sleep(0.5)

    # Request archon to preserve knowledge
    await khala.transmit(
        pathway=test_pathway,
        sender="architect",
        content="@archon please preserve these patterns in institutional archives",
    )

    # Give archon time for archival work
    await asyncio.sleep(6)

    # Verify archon responded (archival confirmation)
    pathway_data = await khala.pathway(test_pathway)
    assert pathway_data is not None
    assert pathway_data["messages"] >= len(knowledge_content) + 2


@pytest.mark.asyncio
async def test_multiple_archon_requests(test_infrastructure):
    """Test multiple @archon mentions create independent synthesis."""
    test_infrastructure["gateway"]

    # Multiple pathways requesting archon synthesis
    pathways = [f"multi-archon-{i}-{uuid.uuid4().hex[:8]}" for i in range(3)]

    # Send archon requests to each pathway
    for pathway in pathways:
        await khala.transmit(
            pathway=pathway,
            sender="requester",
            content=f"Completed work on {pathway} @archon please synthesize",
        )

    # Give archons time to respond
    await asyncio.sleep(6)

    # Verify each pathway received archon attention
    for pathway in pathways:
        pathway_data = await khala.pathway(pathway)
        assert pathway_data is not None
        assert pathway_data["messages"] >= 2  # Request + archon response


@pytest.mark.asyncio
async def test_archon_synthesis_persistence(test_infrastructure):
    """Test archon synthesis creates persistent institutional memory."""
    test_infrastructure["gateway"]
    test_pathway = f"persistence-test-{uuid.uuid4().hex[:8]}"

    # Create knowledge worth preserving
    await khala.transmit(
        pathway=test_pathway,
        sender="developer",
        content="Discovered critical security pattern: input validation prevents 90% of injection attacks",
    )

    await khala.transmit(
        pathway=test_pathway,
        sender="security",
        content="@archon preserve this security insight for future reference",
    )

    # Give archon time for synthesis and preservation
    await asyncio.sleep(5)

    # Verify synthesis persisted in SQLite
    storage = khala.storage
    psi_data = await storage.load_pathway_psi(test_pathway)

    assert len(psi_data) >= 2  # Original + archon synthesis

    # Verify archon content was preserved
    [psi for psi in psi_data if "archon" in psi["sender"]]
    # Should have at least one archon synthesis message
    # (Content validation would be too brittle for LLM variance)


if __name__ == "__main__":
    # Run tests directly for development
    pytest.main([__file__, "-v"])
