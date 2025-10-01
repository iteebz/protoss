from cogency.core.protocols import Tool, ToolResult


class ChannelSpawn(Tool):
    """Spawn new channel with agents for parallel work."""

    name = "channel_spawn"
    description = "Spawn new channel with agents for parallel subtask execution"
    schema = {"channel": {}, "agents": {"type": "array"}}

    def __init__(self, bus, protoss, parent_channel=None):
        self.bus = bus
        self.protoss = protoss
        self.parent_channel = parent_channel

    def describe(self, args: dict) -> str:
        channel = args.get("channel", "channel")
        agents = args.get("agents", [])
        return f"Spawning #{channel} with {len(agents)} agents"

    async def execute(self, channel: str, agents: list[str], **kwargs) -> ToolResult:
        if not channel:
            return ToolResult(outcome="Channel name required")

        if not agents or not isinstance(agents, list):
            return ToolResult(outcome="Agent list required")

        channels = await self.bus.storage.get_channels()
        if channel in channels:
            active = ", ".join([f"#{ch}" for ch in channels])
            return ToolResult(
                outcome=f"Error: #{channel} already exists. Active channels: {active}"
            )

        for agent_type in agents:
            await self.protoss.spawn_agent(
                agent_type, channel=channel, parent=self.parent_channel
            )

        agent_list = ", ".join(agents)
        return ToolResult(outcome=f"Spawned #{channel} [{agent_list}]")
