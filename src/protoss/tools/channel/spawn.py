from cogency.core.protocols import Tool, ToolResult
from ...lib.spawn import build_spawn_context


class ChannelSpawn(Tool):
    """Spawn new channel with fresh team for parallel work."""

    name = "channel_spawn"
    description = (
        "Spawn new #channel with 3-agent squad for parallel subtask execution."
    )
    schema = {
        "channel": {"description": "Name of the new channel"},
        "task": {"description": "Specific task for the new channel to work on"},
    }

    def __init__(self, bus, protoss, parent_channel=None):
        self.bus = bus
        self.protoss = protoss
        self.parent_channel = parent_channel

    def describe(self, args: dict) -> str:
        channel = args.get("channel", "channel")
        return f"Spawning #{channel} with fresh team"

    async def execute(self, channel: str, task: str, **kwargs) -> ToolResult:
        if not channel:
            return ToolResult(outcome="Channel name required")

        if not task:
            return ToolResult(outcome="Task description required")

        channels = await self.bus.storage.get_channels()
        if channel in channels:
            active = ", ".join([f"#{ch}" for ch in channels])
            return ToolResult(
                outcome=f"Error: #{channel} already exists. Active channels: {active}"
            )

        # Build spawn context with topology
        spawn_context = await build_spawn_context(self.bus.storage, channel)
        content = f"{spawn_context}\n\n{task}"

        # Send task with spawn context as first message
        await self.bus.send("human", content, channel)

        # Always spawn 3 agents: zealot, sentinel, harbinger
        for agent_type in ["zealot", "sentinel", "harbinger"]:
            await self.protoss.spawn_agent(
                agent_type, channel=channel, parent=self.parent_channel
            )

        return ToolResult(
            outcome=f"Spawned #{channel} [zealot, sentinel, harbinger] - task: {task}"
        )
