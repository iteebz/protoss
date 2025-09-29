"""Agent management tools for protoss infrastructure."""

import asyncio
import websockets
import json

from cogency.core.protocols import Tool, ToolResult
from ...lib.paths import get_protoss_dir


class AgentSpawn(Tool):
    """Spawn a new agent in a channel."""

    name = "agent_spawn"
    description = "Spawn a new agent of specified type in a channel"
    schema = {
        "agent_type": {
            "type": "string",
            "description": "Type of agent to spawn (arbiter, probe, zealot, etc)",
        },
        "channel": {"type": "string", "description": "Channel to spawn agent in"},
        "coordination_id": {
            "type": "string",
            "optional": True,
            "description": "Coordination ID for task context",
        },
    }

    def describe(self, args: dict) -> str:
        """Human-readable action description."""
        agent_type = args.get("agent_type", "unknown")
        channel = args.get("channel", "unknown")
        return f"Spawning {agent_type} agent in channel '{channel}'"

    async def execute(
        self, agent_type: str, channel: str, coordination_id: str = None, **kwargs
    ) -> ToolResult:
        if not agent_type:
            return ToolResult(outcome="Agent type cannot be empty")

        if not channel:
            return ToolResult(outcome="Channel cannot be empty")

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

            # Send agent spawn event to bus
            async with websockets.connect(bus_url) as websocket:
                event = {
                    "type": "agent_spawn",
                    "agent_type": agent_type,
                    "channel": channel,
                    "coordination_id": coordination_id,
                }
                await websocket.send(json.dumps(event))

                # Wait for confirmation
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                result = json.loads(response)

                if result.get("success"):
                    outcome = f"Spawned {agent_type} agent in channel '{channel}'"
                    if coordination_id:
                        outcome += f" with coordination_id {coordination_id}"
                    return ToolResult(outcome=outcome)
                else:
                    return ToolResult(
                        outcome=f"Failed to spawn agent: {result.get('error', 'Unknown error')}"
                    )

        except asyncio.TimeoutError:
            return ToolResult(outcome="Timeout spawning agent - bus may be down")
        except Exception as e:
            return ToolResult(outcome=f"Error spawning agent: {str(e)}")


class AgentList(Tool):
    """List all active agents."""

    name = "agent_list"
    description = "List all active agents across channels"
    schema = {
        "channel": {
            "type": "string",
            "optional": True,
            "description": "Filter by specific channel",
        }
    }

    def describe(self, args: dict) -> str:
        """Human-readable action description."""
        channel = args.get("channel")
        if channel:
            return f"Listing agents in channel '{channel}'"
        return "Listing all active agents"

    async def execute(self, channel: str = None, **kwargs) -> ToolResult:
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

            # Query bus for agents
            async with websockets.connect(bus_url) as websocket:
                event = {"type": "agent_list"}
                if channel:
                    event["channel"] = channel
                await websocket.send(json.dumps(event))

                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                result = json.loads(response)

                if result.get("success"):
                    agents = result.get("agents", [])
                    if agents:
                        agent_info = "\n".join(
                            [
                                f"- {agent['type']} in #{agent['channel']} (pid: {agent.get('pid', 'unknown')})"
                                for agent in agents
                            ]
                        )
                        return ToolResult(
                            outcome=f"Found {len(agents)} active agents",
                            content=agent_info,
                        )
                    else:
                        return ToolResult(outcome="No active agents found")
                else:
                    return ToolResult(
                        outcome=f"Failed to list agents: {result.get('error', 'Unknown error')}"
                    )

        except asyncio.TimeoutError:
            return ToolResult(outcome="Timeout listing agents - bus may be down")
        except Exception as e:
            return ToolResult(outcome=f"Error listing agents: {str(e)}")
