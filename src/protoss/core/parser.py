"""Pure constitutional summoning - no ceremony."""

import re
from typing import List
from dataclasses import dataclass


@dataclass
class Signal:
    """Base class for all constitutional signals."""

    pass


@dataclass
class MentionSignal(Signal):
    """Represents an @mention of an agent or perspective."""

    agent_name: str


@dataclass
class SpawnSignal(Signal):
    """Represents an @spawn request for an agent type."""

    agent_type: str


@dataclass
class CompletionSignal(Signal):
    """Represents a !complete signal."""

    pass


@dataclass
class DespawnSignal(Signal):
    """Represents a !despawn signal."""

    pass


@dataclass
class ArchiveForReviewSignal(Signal):
    """Represents an !archive_for_review request.
    The content is the work artifact to be archived.
    """

    summary: str


@dataclass
class ReviewSignal(Signal):
    """Represents a !review <review_id> request.
    This is a generic call for review.
    """

    review_id: str


@dataclass
class ReviewingSignal(Signal):
    """Represents a !reviewing <review_id> signal.
    An agent declares it is taking on a review.
    """

    review_id: str


@dataclass
class ReviewedSignal(Signal):
    """Represents a !reviewed <review_id> [judgment] signal.
    An agent declares it has completed a review.
    """

    review_id: str
    judgment: str


@dataclass
class GetArtifactSignal(Signal):
    """Represents a get_artifact <review_id> request to the Archon."""

    review_id: str


def parse_signals(content: str) -> List[Signal]:
    """Parses message content for all constitutional signals."""
    signals: List[Signal] = []

    # Extract @mentions
    for match in re.finditer(r"@(\w+)", content):
        agent_name = match.group(1)
        signals.append(MentionSignal(agent_name=agent_name.lower()))

    # Extract @spawn requests
    for match in re.finditer(r"@spawn\s+(\w+)", content, re.IGNORECASE):
        agent_type = match.group(1)
        signals.append(SpawnSignal(agent_type=agent_type.lower()))

    # Extract !complete signal
    if "!complete" in content.lower():
        signals.append(CompletionSignal())

    # Extract !despawn signal
    if "!despawn" in content.lower():
        signals.append(DespawnSignal())

    # Extract !archive_for_review signal
    archive_match = re.search(r"!archive_for_review\s*(.*)", content, re.IGNORECASE)
    if archive_match:
        summary = archive_match.group(1).strip()
        signals.append(ArchiveForReviewSignal(summary=summary))

    # Extract !review <review_id> signal
    review_match = re.search(r"!review\s*(\S+)", content, re.IGNORECASE)
    if review_match:
        review_id = review_match.group(1).strip()
        signals.append(ReviewSignal(review_id=review_id))

    # Extract !reviewing <review_id> signal
    reviewing_match = re.search(r"!reviewing\s*(\S+)", content, re.IGNORECASE)
    if reviewing_match:
        review_id = reviewing_match.group(1).strip()
        signals.append(ReviewingSignal(review_id=review_id))

    # Extract !reviewed <review_id> [judgment] signal
    reviewed_match = re.search(r"!reviewed\s*(\S+)\s*(.*)", content, re.IGNORECASE)
    if reviewed_match:
        review_id = reviewed_match.group(1).strip()
        judgment = reviewed_match.group(2).strip()
        signals.append(ReviewedSignal(review_id=review_id, judgment=judgment))

    # Extract get_artifact <review_id> signal
    get_artifact_match = re.search(r"get_artifact\s*(\S+)", content, re.IGNORECASE)
    if get_artifact_match:
        review_id = get_artifact_match.group(1).strip()
        signals.append(GetArtifactSignal(review_id=review_id))

    return signals
