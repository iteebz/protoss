"""Tests for constitutional claim management."""

from protoss.core.claim import Claims


def test_claim_creates_unique_id():
    """Claims generate unique identifiers."""
    claims = Claims()

    claim_id1 = claims.claim("agent1", "coord1", "task1")
    claim_id2 = claims.claim("agent2", "coord1", "task2")

    assert claim_id1 != claim_id2
    assert len(claim_id1) == 8  # UUID truncated


def test_claim_stores_metadata():
    """Claims store agent, coordination, and content."""
    claims = Claims()

    claim_id = claims.claim("zealot-a1b2", "coord-123", "build sentiment engine")
    claim = claims.get(claim_id)

    assert claim.agent_id == "zealot-a1b2"
    assert claim.coordination_id == "coord-123"
    assert claim.content == "build sentiment engine"
    assert claim.status == "active"


def test_complete_validates_sovereignty():
    """Only claiming agent can complete their claim."""
    claims = Claims()

    claim_id = claims.claim("agent1", "coord1", "task1")

    # Wrong agent cannot complete
    assert claims.complete(claim_id, "agent2") is False

    # Claiming agent can complete
    assert claims.complete(claim_id, "agent1") is True

    claim = claims.get(claim_id)
    assert claim.status == "complete"


def test_complete_invalid_claim():
    """Completing nonexistent claim returns false."""
    claims = Claims()

    assert claims.complete("invalid-id", "agent1") is False


def test_get_nonexistent_claim():
    """Getting nonexistent claim returns None."""
    claims = Claims()

    assert claims.get("invalid-id") is None
