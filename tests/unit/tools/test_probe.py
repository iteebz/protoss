from unittest.mock import AsyncMock, patch
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

    # Mock cogency Agent
    async def mock_agent_response(content):
        yield {
            "type": "respond",
            "content": '{"command": "create_channel", "args": {"channel_name": "refactor-auth-py"}}',
        }

    with patch("protoss.tools.probe.Agent") as mock_agent_class:
        mock_agent = mock_agent_response
        mock_agent_class.return_value = mock_agent

        await probe.execute(event, mock_bus)

    # Verify channel creation message
    mock_bus.transmit.assert_any_call(
        channel="refactor-auth-py",
        sender="probe",
        event_type="system_message",
        content="Channel 'refactor-auth-py' created by probe.",
        coordination_id="coord-1",
    )
    # Only channel creation message should be sent with new LLM-based probe
    assert mock_bus.transmit.call_count == 1


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

    # Mock cogency Agent
    async def mock_agent_response(content):
        yield {
            "type": "respond",
            "content": '{"command": "create_channel", "args": {"channel_name": "feature-x"}}',
        }

    with patch("protoss.tools.probe.Agent") as mock_agent_class:
        mock_agent = mock_agent_response
        mock_agent_class.return_value = mock_agent

        await probe.execute(event, mock_bus)

    # Verify channel creation message
    mock_bus.transmit.assert_any_call(
        channel="feature-x",
        sender="probe",
        event_type="system_message",
        content="Channel 'feature-x' created by probe.",
        coordination_id="coord-2",
    )
    # Only channel creation message should be sent with new LLM-based probe
    assert mock_bus.transmit.call_count == 1


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

    # Mock cogency Agent
    async def mock_agent_response(content):
        yield {"type": "respond", "content": '{"command": "unrecognized", "args": {}}'}

    with patch("protoss.tools.probe.Agent") as mock_agent_class:
        mock_agent = mock_agent_response
        mock_agent_class.return_value = mock_agent

        await probe.execute(event, mock_bus)

    # Unrecognized command should send error message
    mock_bus.transmit.assert_called_once_with(
        channel="alpha",
        sender="probe",
        event_type="system_message",
        content="Probe: Unrecognized or unimplemented command: 'this is a regular message without a probe command.'.",
        coordination_id="coord-3",
    )
