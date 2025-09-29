import asyncio
import pytest
from protoss.core.bus import Bus


async def get_claim_event(bus: Bus) -> bool:
    """Task to listen for a claim registration event."""
    try:
        async for event in bus.subscribe(event_type="system_message"):
            if "Claim" in event.content and "registered" in event.content:
                return True
    except asyncio.CancelledError:
        return False


@pytest.mark.asyncio
async def test_agent_claims_task_in_harness(protoss_harness, mock_cogency_agent):
    """
    TRIAL: An agent, when presented with a vision, must declare its
    intention to act by making a constitutional !claim.
    """
    bus, spawn_agent = protoss_harness

    coordination_id = "trial-of-claims-1"
    task_description = "build monument"

    # ARRANGE: Spawn the agent.
    agent, agent_task = await spawn_agent(
        agent_type="zealot", channel="human", coordination_id=coordination_id
    )

    # Configure the mock cogency agent to call the protoss_claim tool.
    async def mock_cogency_agent_call(content_arg):
        yield {
            "type": "tool_code",
            "content": f"protoss_claim(task='{task_description}', coordination_id='{coordination_id}')",
        }

    mock_cogency_agent.side_effect = mock_cogency_agent_call

    # ACT: Set up the listener for the expected outcome *before* the action.
    listener_task = asyncio.create_task(get_claim_event(bus))

    # Transmit a message to the agent to trigger its cogency processing.
    await bus.transmit(
        channel="human",
        sender="human_client",
        event_type="agent_message",
        content="Build a monument to the fallen!",
        coordination_id=coordination_id,
    )

    # Give the agent time to process the message and respond.
    await asyncio.sleep(0.1)

    # ASSERT: The listener task must complete successfully within a timeout.
    try:
        claim_registered = await asyncio.wait_for(listener_task, timeout=1.0)
    except asyncio.TimeoutError:
        claim_registered = False

    assert claim_registered, "The agent failed to make a constitutional claim."

    # We can also directly inspect the Bus Kernel's state.
    assert len(bus.claims.claims) == 1
    claim = list(bus.claims.claims.values())[0]
    assert claim.coordination_id == coordination_id
    assert claim.content == task_description
    assert claim.status == "active"
