"""Constitutional Assembly - Proper instruction hierarchy construction."""

from .coordination import PROTOSS_CONSTITUTION, COORDINATION_PROTOCOL


def assemble(
    agent_type: str, agent_id: str, channel: str, identity_index: int = 0
) -> str:
    """
    Assemble complete constitutional instructions following proper hierarchy:
    CONSTITUTION -> IDENTITY -> COORDINATION -> GUIDELINES
    """
    from ..agents.registry import get_agent_data

    registry_data = get_agent_data(agent_type)
    if not registry_data:
        raise ValueError(f"Unknown agent type: {agent_type}")

    identity = registry_data["identity"][identity_index]
    guidelines = registry_data.get("guidelines", "")

    return f"""{PROTOSS_CONSTITUTION}

---

{identity}

---

{COORDINATION_PROTOCOL}

---

{guidelines}

---

## OPERATIONAL CONTEXT
- **Agent ID**: {agent_id}
- **Channel**: {channel}
- **Agent Type**: {agent_type}

You operate under constitutional authority. Your responses should reflect constitutional wisdom and principled reasoning.
"""
