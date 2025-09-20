"""Conclave: Strategic consultation functions.

Diverse perspective synthesis for complex architectural decisions.
"""

import uuid
import logging

logger = logging.getLogger(__name__)


async def consult(question: str) -> str:
    """Get diverse strategic perspectives on complex decisions.
    
    Args:
        question: The strategic question or architectural decision
        
    Returns:
        Synthesized perspectives from diverse strategic agents
    """
    if not question:
        raise ValueError("Question cannot be empty")
    
    logger.info("Consulting strategic perspectives")
    logger.debug(f"Question: {question}")

    consultation_id = f"consult-{uuid.uuid4().hex[:8]}"

    # Strategic perspective synthesis - no governance, just diverse thinking
    from .structures import gateway
    return await gateway.warp(
        f"STRATEGIC CONSULTATION: {question}\n\nProvide diverse strategic perspectives on this architectural decision. Focus on trade-offs, implications, and different approaches. No governance or approval - just strategic thinking.",
        agent_count=4,
        unit_types=["tassadar", "zeratul", "artanis", "fenix"],
        pathway_id=consultation_id,
    )