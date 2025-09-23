"""Cathedral interface integration tests for the event-driven architecture."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
import uuid

from protoss.core.protoss import Protoss
from protoss.core.bus import Bus
from protoss.core.khala import Khala
from protoss.core import gateway  # To mock spawn_agent


@pytest.fixture
async def running_bus():
    """Fixture to provide a running Bus instance for integration tests."""
    bus = Bus(port=9998)  # Use a different port to avoid conflicts
    await bus.start()
    yield bus
    await bus.stop()


@pytest.mark.asyncio
async def test_cathedral_interface_with_mock_agent(running_bus):
    """
    Integration test: Protoss seeds vision, a mock agent spawns and signals completion.
    """
    vision = "integrate and conquer"
    coordination_id = str(uuid.uuid4())

    # Mock gateway.spawn_agent to simulate an agent that immediately completes
    async def mock_spawn_agent(agent_type, channel, bus_url):
        # Simulate an agent connecting and sending a completion event
        mock_agent_khala = Khala(bus_url=bus_url)
        await mock_agent_khala.connect(client_id=f"{agent_type}-mock")

        # Send a coordination_complete event directly
        await mock_agent_khala.send(
            channel=channel,
            sender="system",  # Or the mock agent itself
            event_type="coordination_complete",
            coordination_id=coordination_id,
            event_payload={"result": "Mock Agent Completed Vision"},
        )
        await mock_agent_khala.disconnect()

    with patch.object(
        gateway, "spawn_agent", new_callable=AsyncMock, side_effect=mock_spawn_agent
    ) as mock_spawn:
        # Patch Protoss to use our specific coordination_id for predictable mocking
        with patch.object(Protoss, "coordination_id", new=coordination_id):
            async with Protoss(vision, port=9998) as swarm:
                # The vision seed will trigger mock_spawn_agent
                mock_spawn.assert_called_once()

                # Iterate through events to find the completion
                received_events = []
                async for event in swarm:
                    received_events.append(event)
                    if event["type"] == "coordination_complete":
                        break

                assert any(e["type"] == "vision_seed" for e in received_events)
                assert any(
                    e["type"] == "coordination_complete" for e in received_events
                )

                completion_event = next(
                    e for e in received_events if e["type"] == "coordination_complete"
                )
                assert (
                    completion_event["payload"]["result"]
                    == "Mock Agent Completed Vision"
                )
                assert completion_event["coordination_id"] == coordination_id

                # Also test the await swarm.completion() syntax
                result = await swarm.completion()
                assert result == "Mock Agent Completed Vision"


@pytest.mark.asyncio
async def test_cathedral_event_streaming(running_bus):
    """
    Integration test: Protoss streams various events from a mock agent.
    """
    vision = "stream all events"
    coordination_id = str(uuid.uuid4())

    async def mock_spawn_agent_streaming(agent_type, channel, bus_url):
        mock_agent_khala = Khala(bus_url=bus_url)
        await mock_agent_khala.connect(client_id=f"{agent_type}-stream-mock")

        # Simulate a sequence of events
        await mock_agent_khala.send(
            channel=channel,
            sender=f"{agent_type}-stream-mock",
            event_type="agent_spawn",
            coordination_id=coordination_id,
            event_payload={"agent_id": f"{agent_type}-stream-mock"},
        )
        await asyncio.sleep(0.01)  # Allow bus to process
        await mock_agent_khala.send(
            channel=channel,
            sender=f"{agent_type}-stream-mock",
            event_type="agent_message",
            coordination_id=coordination_id,
            content="Thinking hard...",
            event_payload={"thought": "complex calculation"},
        )
        await asyncio.sleep(0.01)
        await mock_agent_khala.send(
            channel=channel,
            sender=f"{agent_type}-stream-mock",
            event_type="agent_despawn",
            coordination_id=coordination_id,
            event_payload={"agent_id": f"{agent_type}-stream-mock"},
        )
        await asyncio.sleep(0.01)
        await mock_agent_khala.send(
            channel=channel,
            sender="system",
            event_type="coordination_complete",
            coordination_id=coordination_id,
            event_payload={"result": "Streaming complete"},
        )
        await mock_agent_khala.disconnect()

    with patch.object(
        gateway,
        "spawn_agent",
        new_callable=AsyncMock,
        side_effect=mock_spawn_agent_streaming,
    ) as mock_spawn:
        with patch.object(Protoss, "coordination_id", new=coordination_id):
            received_events = []
            async with Protoss(vision, port=9998) as swarm:
                mock_spawn.assert_called_once()
                async for event in swarm:
                    received_events.append(event)
                    if event["type"] == "coordination_complete":
                        break

            event_types = [e["type"] for e in received_events]
            assert "vision_seed" in event_types
            assert "agent_spawn" in event_types
            assert "agent_message" in event_types
            assert "agent_despawn" in event_types
            assert "coordination_complete" in event_types

            assert (
                next(e for e in received_events if e["type"] == "agent_message")[
                    "content"
                ]
                == "Thinking hard..."
            )
            assert (
                next(
                    e for e in received_events if e["type"] == "coordination_complete"
                )["payload"]["result"]
                == "Streaming complete"
            )
