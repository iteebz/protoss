"""Cross-channel message routing."""

import re
from typing import Tuple, Optional


def parse_route(content: str) -> Tuple[Optional[str], str]:
    """Parse message for #channel: routing directive.

    Returns:
        (target_channel, message_body) if routing found, else (None, content)

    Examples:
        "#main: found answer" -> ("main", "found answer")
        "I'm blocked, #human: need help" -> ("human", "need help")
        "#protoss-dev: hyphenated channels work" -> ("protoss-dev", "hyphenated channels work")
        "normal message" -> (None, "normal message")
    """
    match = re.search(r"#([\w-]+):\s*(.+)", content)
    if match:
        return match.group(1), match.group(2)
    return None, content


def format_stub(target: str, message: str, max_len: int = 50) -> str:
    """Format forwarding stub for source channel."""
    preview = message[:max_len] + ("..." if len(message) > max_len else "")
    return f"→ #{target}: {preview}"
