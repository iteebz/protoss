"""Constitutional channel naming utilities.

The Khala operates on structured channel names following {purpose}:{identifier}:{status}:

Channel Types:
- nexus: Prime coordination channel where all human visions begin
- task:{slug}-{uuid}:active: Work coordination channels created by @probe
- query:{uuid}:active: Human questions via CLI ask command
- conclave:{uuid}:active: Sacred Four deliberation channels
- general: Default fallback channel for unspecified coordination

Status Lifecycle:
- active: Current coordination in progress (default)
- complete: Work finished, agents despawned
- archived: Historical record, no active coordination

The taxonomy ensures channels are self-documenting and enables natural
coordination patterns without ceremony.
"""

import uuid


def channel(purpose: str, identifier: str, status: str = "active") -> str:
    """Generate constitutional channel names.

    Args:
        purpose: Channel purpose (task, query, conclave, etc.)
        identifier: Unique identifier (slug, uuid, etc.)
        status: Channel status (active, complete, archived)

    Returns:
        Formatted channel name following {purpose}:{identifier}:{status} pattern

    Examples:
        channel("task", "auth-refactor")           # task:auth-refactor:active
        channel("query", "abc123")                 # query:abc123:active
        channel("conclave", "def456")              # conclave:def456:active
        channel("task", "auth-refactor", "done")   # task:auth-refactor:done
    """
    return f"{purpose}:{identifier}:{status}"


def uuid_short() -> str:
    """Generate short UUID for channel identifiers."""
    return uuid.uuid4().hex[:8]


def task_channel(slug: str, status: str = "active") -> str:
    """Generate task coordination channel."""
    return channel("task", f"{slug}-{uuid_short()}", status)


def query_channel() -> str:
    """Generate query channel for human questions."""
    return channel("query", uuid_short())


def conclave_channel() -> str:
    """Generate conclave channel for Sacred Four deliberation."""
    return channel("conclave", uuid_short())
