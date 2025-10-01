from cogency.core.protocols import Tool, ToolResult


class ChannelList(Tool):
    """List active channels."""

    name = "channel_list"
    description = "List all active channels"
    schema = {}

    def __init__(self, bus):
        self.bus = bus

    def describe(self, args: dict) -> str:
        return "Listing active channels"

    async def execute(self, **kwargs) -> ToolResult:
        channels = await self.bus.storage.get_channels()
        if not channels:
            return ToolResult(outcome="No active channels")

        content = "\n".join([f"#{ch}" for ch in channels])
        return ToolResult(
            outcome=f"Found {len(channels)} active channels", content=content
        )
