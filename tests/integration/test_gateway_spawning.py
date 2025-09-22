"""Integration tests for Gateway spawning functionality."""

import json
from unittest.mock import patch, AsyncMock, call
import pytest


@pytest.mark.asyncio
async def test_gateway_handles_vision():
    """Gateway spawns agent on vision."""
    from protoss.core.gateway import Gateway
    from protoss.core.config import Config

    gateway = Gateway(Config())

    with patch.object(gateway, "_spawn_process", new_callable=AsyncMock) as mock_spawn:
        vision_content = "build auth"
        vision_msg_payload = {
            "type": "vision",
            "channel": "test",
            "content": vision_content,
            "params": {},
        }
        wrapped_msg = {
            "type": "msg",
            "channel": "gateway_commands",
            "content": json.dumps(vision_msg_payload),
        }

        await gateway._handle_message(json.dumps(wrapped_msg))

        calls = [
            call(
                agent_type="archon",
                channel_id="test",
                task=f"seed channel for: {vision_content}",
                agent_params={"action": "seed_channel"},
            ),
            call(
                agent_type="zealot",
                channel_id="test",
                task=vision_content,
            ),
        ]
        mock_spawn.assert_has_calls(calls, any_order=True)


@pytest.mark.asyncio
async def test_gateway_handles_mention_spawn():
    """Gateway spawns on @mention."""
    from protoss.core.gateway import Gateway
    from protoss.core.config import Config

    gateway = Gateway(Config())
    gateway.channel_tasks["test_channel"] = "existing task"

    with patch.object(gateway, "_spawn_process", new_callable=AsyncMock) as mock_spawn:
        message_with_mention = {
            "type": "msg",
            "channel": "test_channel",
            "sender": "some_agent",
            "content": "we need help from @archon to proceed",
        }

        await gateway._handle_message(json.dumps(message_with_mention))

        mock_spawn.assert_called_once_with(
            agent_type="archon",
            channel_id="test_channel",
            task="we need help from @archon to proceed",
            agent_params={"action": "respond_to_mention"},
        )
