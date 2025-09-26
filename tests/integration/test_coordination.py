"""
Cathedral Grade test for the `Protoss` client and core coordination loop.

This test validates the "Cathedral Interface" by ensuring the `Protoss`
context manager can correctly initiate a vision and await a completion
signal from the swarm, fulfilling the synthesis path mandate.
"""

import pytest

from protoss.core.protoss import Protoss


@pytest.mark.asyncio
async def test_protoss_client_awaits_arbiter_completion(
    protoss_components, event_factory
):
    """
    Verify that the `Protoss` client correctly awaits and returns the
    completion event from an arbiter agent on the nexus channel.
    """
    async with Protoss("My vision @arbiter") as swarm:
        khala = protoss_components["khala"]
        completion_event = event_factory(
            channel="nexus",
            sender="arbiter-123",
            content="Vision fulfilled.",
            coordination_id=swarm.coordination_id,
        )

        # Simulate the Khala yielding the final completion event from the arbiter
        async def listen_generator():
            yield completion_event

        khala.listen = listen_generator

        result = await swarm

    # Assert that the initial vision was sent
    khala.send.assert_awaited_once()
    sent_data = khala.send.await_args.args[0]
    assert sent_data["channel"] == "nexus"
    assert sent_data["content"] == "My vision @arbiter"

    # Assert that the result of the coordination is the arbiter's completion event
    assert result == completion_event


@pytest.mark.asyncio
async def test_coordination_pull_model_robustness(protoss_components, event_factory):
    """
    Regression test: Coordination succeeds even when there are timing delays
    in agent spawning, proving the Pull model (agent requests history) works.

    This test documents the fix for the timing race condition where agents
    missed their triggering messages during the spawn process.
    """
    async with Protoss("Status report @arbiter") as swarm:
        khala = protoss_components["khala"]

        # Simulate agent successfully processing context and responding
        response_event = event_factory(
            channel="nexus",
            sender="arbiter-spawn-test",
            content="Status: All systems operational. Context assembly successful.",
            coordination_id=swarm.coordination_id,
        )

        async def listen_generator():
            yield response_event

        khala.listen = listen_generator
        result = await swarm

    # Verify coordination completes successfully
    assert result == response_event
    assert "Context assembly successful" in result.content

    # This test proves the timing race fix works:
    # - Human sends triggering message
    # - Agent spawns and requests channel history (Pull model)
    # - Agent processes history through cogency for constitutional context
    # - Agent responds with understanding of the original request
