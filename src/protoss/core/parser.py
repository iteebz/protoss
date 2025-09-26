"""Pure constitutional summoning - no ceremony."""

import re
from typing import List
from .protocols import Signal, Mention, Despawn, Emergency
from protoss.agents.registry import get_agent_names


def signals(content: str) -> List:
    """
    Parses message content for signals defined in the canonical doctrine.
    As per emergence.md, only @mentions and sacred guardrails are parsed.
    """
    signals_found: List[Signal] = []

    # Dynamically get known agent names
    KNOWN_AGENTS = get_agent_names()

    # @mentions for known agents
    for agent_name in KNOWN_AGENTS:
        # Regex to match @agent_name as a standalone word, case-insensitive
        # Ensures @ is preceded by non-alphanumeric/underscore or start of string
        # Ensures agent_name is followed by non-alphanumeric/underscore or end of string
        pattern = (
            r"(?:^|(?<=[^a-zA-Z0-9_]))@"
            + re.escape(agent_name)
            + r"(?=[^a-zA-Z0-9_]|$)"
        )
        for match in re.finditer(pattern, content, re.IGNORECASE):
            signals_found.append(Mention(agent_name=agent_name.lower()))

    # Sacred guardrails
    if "!despawn" in content.lower():
        signals_found.append(Despawn())

    if "!emergency" in content.lower():
        signals_found.append(Emergency())

    return signals_found
