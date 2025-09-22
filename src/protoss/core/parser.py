"""Pure constitutional summoning - no ceremony."""

import re
from typing import List
from .protocols import Signal, Signals


def parse_signals(content: str) -> List[Signal]:
    """Parses message content for all constitutional signals."""
    signals: List[Signal] = []

    # Extract @mentions
    for match in re.finditer(r"@(\w+)", content):
        agent_name = match.group(1)
        signals.append(Signal.Mention(agent_name=agent_name.lower()))

    # Extract @spawn requests
    for match in re.finditer(r"@spawn\s+(\w+)", content, re.IGNORECASE):
        agent_type = match.group(1)
        signals.append(Signal.Spawn(agent_type=agent_type.lower()))

    # Extract !complete signal
    if "!complete" in content.lower():
        signals.append(Signal.Completion())

    # Extract !despawn signal
    if "!despawn" in content.lower():
        signals.append(Signal.Despawn())

    # Extract !archive signal
    archive_match = re.search(r"!archive\s*(.*)", content, re.IGNORECASE)
    if archive_match:
        summary = archive_match.group(1).strip()
        signals.append(Signal.Archive(summary=summary))

    # Extract !review <review_id> signal
    review_match = re.search(r"!review\s*(\S+)", content, re.IGNORECASE)
    if review_match:
        review_id = review_match.group(1).strip()
        signals.append(Signal.Review(review_id=review_id))

    # Extract !reviewing <review_id> signal
    reviewing_match = re.search(r"!reviewing\s*(\S+)", content, re.IGNORECASE)
    if reviewing_match:
        review_id = reviewing_match.group(1).strip()
        signals.append(Signal.Reviewing(review_id=review_id))

    # Extract !reviewed <review_id> [judgment] signal
    reviewed_match = re.search(r"!reviewed\s*(\S+)\s*(.*)", content, re.IGNORECASE)
    if reviewed_match:
        review_id = reviewed_match.group(1).strip()
        judgment = reviewed_match.group(2).strip()
        signals.append(Signal.Reviewed(review_id=review_id, judgment=judgment))


    return signals
