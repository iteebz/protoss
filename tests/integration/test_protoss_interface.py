"""Integration tests for the Protoss interface."""

import json
from unittest.mock import patch, AsyncMock
import pytest
import websockets


@pytest.mark.asyncio
async def test_protoss_cathedral_interface(config):
    """Cathedral interface works by connecting to Bus and seeding vision."""
    from protoss import Protoss

    mock_websocket_instance = AsyncMock()
    mock_websocket_instance.send = AsyncMock()
    mock_websocket_instance.close = AsyncMock()
    mock_websocket_instance.recv.return_value = json.dumps({"type": "engine_ack"})

    # Mock the async context manager behavior
    mock_websocket_instance.__aenter__ = AsyncMock(return_value=mock_websocket_instance)
    mock_websocket_instance.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "websockets.connect",
        new_callable=AsyncMock,
        return_value=mock_websocket_instance,
    ):
        async with Protoss("test vision", config=config) as swarm:
            assert swarm.vision == "test vision"
            assert swarm._channel_id.startswith("cathedral_")

            # Assert websockets.connect was called with the correct URI
            websockets.connect.assert_called_once_with(
                f"{config.bus_url}/protoss_engine"
            )

            # Assert the sequence of sends
            from unittest.mock import call

            vision_content = {
                "type": "vision",
                "channel": swarm._channel_id,
                "content": "test vision",
                "params": {},
            }
            message_to_gateway = {
                "type": "msg",
                "channel": "gateway_commands",
                "content": vision_content,
            }
            calls = [
                call(json.dumps({"type": "engine_req"})),
                call(json.dumps(message_to_gateway)),
            ]
            mock_websocket_instance.send.assert_has_calls(calls, any_order=False)

        # Ensure websocket is closed on exit
        mock_websocket_instance.close.assert_called_once()
