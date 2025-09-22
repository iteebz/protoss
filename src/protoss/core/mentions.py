"""Utilities for parsing and sanitizing agent mentions."""

import re
from typing import List, Optional

def extract_mentions(content: str) -> List[str]:
    """Extract @mentions from message content."""
    return re.findall(r"@(\w+(?:-\w+)*)", content)

def _is_specific_agent_mention(mention: str) -> bool:
    """Check if mention targets specific agent (e.g., zealot-abc123)."""
    return "-" in mention and any(
        mention.startswith(agent_type + "-")
        for agent_type in [
            "zealot",
            "archon",
            "conclave",
            "arbiter",
            "tassadar",
            "zeratul",
            "artanis",
            "fenix",
        ]
    )

def resolve_agent_type(base: str) -> str:
    """Map mention prefix to canonical agent type."""
    if base in {"tassadar", "zeratul", "artanis", "fenix"}:
        return "conclave"
    if base == "human":
        return "arbiter"
    return base

def mention_tokens_for_agent(
    agent_type: str,
    message_content: str,
    target_agent_id: Optional[str],
) -> List[str]:
    """Determine which mention tokens apply to a given agent."""

    tokens: List[str] = []

    for mention in extract_mentions(message_content):
        base = mention.split("-", 1)[0]
        resolved = resolve_agent_type(base)

        if target_agent_id:
            if mention == target_agent_id or resolved == agent_type:
                if mention not in tokens:
                    tokens.append(mention)
        else:
            if resolved == agent_type and mention not in tokens:
                tokens.append(mention)

    return tokens

def sanitize_mention_context(content: str, mentions: List[str]) -> str:
    """Strip targeted @mentions from context while preserving message gist."""

    sanitized = content or ""

    if mentions:
        pattern = r"@(?:" + "|".join(re.escape(token) for token in mentions) + r")"
        sanitized = re.sub(pattern, "", sanitized)

    # Normalize whitespace and spacing before punctuation
    sanitized = re.sub(r"\s+", " ", sanitized)
    sanitized = re.sub(r"\s+([,.;:])", r"\1", sanitized)

    return sanitized.strip()
