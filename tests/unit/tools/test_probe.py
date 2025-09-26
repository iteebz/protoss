from unittest.mock import AsyncMock
import pytest

from protoss.core.event import Event
from protoss.tools import probe


@pytest.mark.asyncio
async def test_execute_create_channel_command():
    mock_bus = AsyncMock()
    event = Event(
        type="agent_message",
        channel="alpha",
        sender="zealot",
        coordination_id="coord-1",
        content="@probe create a channel for 'refactor-auth-py'",
    )

    await probe.execute(event, mock_bus)

    # Verify channel creation message
    mock_bus.transmit.assert_any_call(
        channel="refactor-auth-py",
        sender="probe",
        event_type="system_message",
        content="Channel 'refactor-auth-py' created by probe.",
        coordination_id="coord-1",
    )
    # Verify confirmation message to original channel
    mock_bus.transmit.assert_any_call(
        channel="alpha",
        sender="probe",
        event_type="system_message",
        content="Probe command executed: @probe create a channel for 'refactor-auth-py'",
        coordination_id="coord-1",
    )
    assert mock_bus.transmit.call_count == 2


@pytest.mark.asyncio
async def test_execute_create_channel_and_instruct_agent_command():
    mock_bus = AsyncMock()
    event = Event(
        type="agent_message",
        channel="alpha",
        sender="zealot",
        coordination_id="coord-2",
        content="@probe create a channel for 'feature-x' and then instruct '@archon' to begin work'",
    )

    await probe.execute(event, mock_bus)

    # Verify channel creation message
    mock_bus.transmit.assert_any_call(
        channel="feature-x",
        sender="probe",
        event_type="system_message",
        content="Channel 'feature-x' created by probe.",
        coordination_id="coord-2",
    )
    # Verify instruction message to agent in new channel
    mock_bus.transmit.assert_any_call(
        channel="feature-x",
        sender="probe",
        event_type="agent_message",
        content="@archon begin work in channel 'feature-x'.",
        coordination_id="coord-2",
    )
    # Verify confirmation message to original channel
    mock_bus.transmit.assert_any_call(
        channel="alpha",
        sender="probe",
        event_type="system_message",
        content="Probe command executed: @probe create a channel for 'feature-x' and then instruct '@archon' to begin work'",
        coordination_id="coord-2",
    )
    assert mock_bus.transmit.call_count == 3


@pytest.mark.asyncio
async def test_execute_no_probe_command():
    mock_bus = AsyncMock()
    event = Event(
        type="agent_message",
        channel="alpha",
        sender="zealot",
        coordination_id="coord-3",
        content="This is a regular message without a probe command.",
    )

    await probe.execute(event, mock_bus)

    # Only the confirmation message should be sent
    mock_bus.transmit.assert_called_once_with(
        channel="alpha",
        sender="probe",
        event_type="system_message",
        content="Probe command executed: This is a regular message without a probe command.",
        coordination_id="coord-3",
    )
