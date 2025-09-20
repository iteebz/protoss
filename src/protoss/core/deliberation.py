"""Deliberation: Strategic consultation through multi-perspective synthesis.

Diverse perspective synthesis for complex architectural decisions.
"""

import uuid
import logging

logger = logging.getLogger(__name__)


async def consult(question: str, bus=None, conclave=None) -> str:
    """Get diverse strategic perspectives on complex decisions.

    Args:
        question: The strategic question or architectural decision
        bus: Bus instance for coordination (required for agent execution)
        conclave: Callable that returns Conclave instances for each perspective

    Returns:
        Synthesized perspectives from diverse strategic agents
    """
    if not question:
        raise ValueError("Question cannot be empty")

    logger.info("Consulting strategic perspectives")
    logger.debug(f"Question: {question}")

    consultation_id = f"channel-consult-{uuid.uuid4().hex[:8]}"

    if bus is None:
        raise ValueError("Bus instance required for agent coordination")
    if conclave is None:
        raise ValueError(
            "Conclave constructor required for creating perspective agents"
        )

    # Strategic perspective synthesis through multi-agent deliberation

    # Create Sacred Four perspectives
    perspectives = []
    for perspective_name in ["fenix", "artanis", "zeratul", "tassadar"]:
        agent = conclave(perspective_name, f"{perspective_name}-{consultation_id}")
        try:
            response = await agent.execute(
                task=f"STRATEGIC CONSULTATION: {question}\n\nProvide your perspective on this architectural decision. Focus on trade-offs, implications, and different approaches from your constitutional viewpoint.",
                channel_context="",
                channel_id=consultation_id,
                bus=bus,  # Pure dependency injection
            )
            perspectives.append(f"{perspective_name.upper()}: {response}")
        except Exception as e:
            logger.warning(f"Failed to get {perspective_name} perspective: {e}")
            perspectives.append(
                f"{perspective_name.upper()}: [Perspective unavailable]"
            )

    if not perspectives:
        return f"Strategic consultation failed [{consultation_id}]"

    transcript = "\n\n".join(perspectives)
    return (
        f"Strategic consultation complete [{consultation_id}]\n\n"
        f"Multi-perspective synthesis:\n\n{transcript}"
    )
