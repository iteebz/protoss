"""Pure constitutional summoning - no ceremony."""

import re
from typing import List
from .protocols import Signal


def signals(content: str) -> List[Signal]:
    """
    Parses message content for signals defined in the canonical doctrine.
    As per emergence.md, only @mentions and sacred guardrails are parsed.
    """
    signals_found: List[Signal] = []

    # Pillar II: Natural Language as the Medium of Coordination (@mention)
    for match in re.finditer(r"@(\w+)", content):
        agent_name = match.group(1).lower()
        signals_found.append(Signal.Mention(agent_name=agent_name))

    # Section 3.3: The Sacred Guardrails (!despawn, !emergency)
    if "!despawn" in content.lower():
        signals_found.append(Signal.Despawn())

    if "!emergency" in content.lower():
        signals_found.append(Signal.Emergency())

    return signals_found
