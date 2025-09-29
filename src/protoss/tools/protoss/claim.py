"""Protoss claim tool for agents."""

from cogency.core.protocols import Tool, ToolResult
from protoss.core.khala import Khala
from protoss.core.config import Config


class ClaimTool(Tool):
    name = "protoss_claim"
    description = "Register a claim for a task with the Protoss Bus."
    schema = {
        "task": {
            "type": "string",
            "description": "Description of the task being claimed.",
        },
        "coordination_id": {
            "type": "string",
            "description": "The ID of the coordination session.",
        },
    }

    def describe(self, args: dict) -> str:
        return f"Claiming task: {args.get('task')} for coordination {args.get('coordination_id')}"

    async def execute(self, task: str, coordination_id: str, **kwargs) -> ToolResult:
        config = Config()
        khala = Khala(bus_url=config.bus_url)
        try:
            await khala.connect(agent_id="tool_client")
            await khala.send(
                {
                    "type": "tool_output",
                    "channel": "system",  # Tool outputs are system-level events
                    "sender": "tool_client",
                    "coordination_id": coordination_id,
                    "payload": {
                        "tool_name": self.name,
                        "outcome": "success",
                        "args": {"task": task, "coordination_id": coordination_id},
                    },
                }
            )
            return ToolResult(
                outcome=f"Claim for '{task}' in coordination '{coordination_id}' sent to Bus."
            )
        except Exception as e:
            return ToolResult(
                outcome=f"Failed to send claim to Bus: {e}", is_error=True
            )
        finally:
            await khala.disconnect()
