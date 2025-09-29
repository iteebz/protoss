"""Channel management tools for protoss infrastructure."""

import asyncio
import websockets
import json

from cogency.core.protocols import Tool, ToolResult
from ...lib.paths import get_protoss_dir


class ChannelCreate(Tool):
    """Create a new communication channel."""

    name = "channel_create"
    description = "Create a new communication channel for agent coordination"
    schema = {
        "channel": {"type": "string", "description": "Channel name to create"},
        "description": {
            "type": "string",
            "optional": True,
            "description": "Optional channel description",
        },
    }

    def describe(self, args: dict) -> str:
        """Human-readable action description."""
        return f"Creating channel '{args.get('channel', 'unnamed')}'"

    async def execute(
        self, channel: str, description: str = None, **kwargs
    ) -> ToolResult:
        if not channel:
            return ToolResult(outcome="Channel name cannot be empty")

        if not channel.replace("_", "").replace("-", "").isalnum():
            return ToolResult(
                outcome="Channel name must be alphanumeric with underscores/hyphens"
            )

        try:
            # Get bus URL from config
            config_path = get_protoss_dir() / "config.toml"
            if not config_path.exists():
                return ToolResult(
                    outcome="Protoss not configured - run 'protoss config'"
                )

            import tomllib

            with open(config_path, "rb") as f:
                config = tomllib.load(f)

            bus_url = config.get("bus", {}).get("url", "ws://localhost:8765")

            # Send channel creation event to bus
            async with websockets.connect(bus_url) as websocket:
                event = {
                    "type": "channel_create",
                    "channel": channel,
                    "metadata": {"description": description} if description else {},
                }
                await websocket.send(json.dumps(event))

                # Wait for confirmation
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                result = json.loads(response)

                if result.get("success"):
                    outcome = f"Created channel '{channel}'"
                    if description:
                        outcome += f" - {description}"
                    return ToolResult(outcome=outcome)
                else:
                    return ToolResult(
                        outcome=f"Failed to create channel: {result.get('error', 'Unknown error')}"
                    )

        except asyncio.TimeoutError:
            return ToolResult(outcome="Timeout creating channel - bus may be down")
        except Exception as e:
            return ToolResult(outcome=f"Error creating channel: {str(e)}")


class ChannelList(Tool):
    """List all available channels."""

    name = "channel_list"
    description = "List all available communication channels"
    schema = {}

    def describe(self, args: dict) -> str:
        """Human-readable action description."""
        return "Listing all channels"

    async def execute(self, **kwargs) -> ToolResult:
        try:
            # Get bus URL from config
            config_path = get_protoss_dir() / "config.toml"
            if not config_path.exists():
                return ToolResult(
                    outcome="Protoss not configured - run 'protoss config'"
                )

            import tomllib

            with open(config_path, "rb") as f:
                config = tomllib.load(f)

            bus_url = config.get("bus", {}).get("url", "ws://localhost:8765")

            # Query bus for channels
            async with websockets.connect(bus_url) as websocket:
                event = {"type": "channel_list"}
                await websocket.send(json.dumps(event))

                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                result = json.loads(response)

                if result.get("success"):
                    channels = result.get("channels", [])
                    if channels:
                        channel_info = "\n".join([f"- {ch}" for ch in channels])
                        return ToolResult(
                            outcome=f"Found {len(channels)} channels",
                            content=channel_info,
                        )
                    else:
                        return ToolResult(outcome="No channels found")
                else:
                    return ToolResult(
                        outcome=f"Failed to list channels: {result.get('error', 'Unknown error')}"
                    )

        except asyncio.TimeoutError:
            return ToolResult(outcome="Timeout listing channels - bus may be down")
        except Exception as e:
            return ToolResult(outcome=f"Error listing channels: {str(e)}")
