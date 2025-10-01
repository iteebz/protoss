from cogency.core.protocols import Tool, ToolResult


class ChannelRead(Tool):
    """Read transcript from another channel."""

    name = "channel_read"
    description = "Read conversation transcript from another channel"
    schema = {"channel": {}}

    def __init__(self, bus):
        self.bus = bus

    def describe(self, args: dict) -> str:
        return f"Reading #{args.get('channel', 'channel')}"

    async def execute(self, channel: str, **kwargs) -> ToolResult:
        if not channel:
            return ToolResult(outcome="Channel name required")

        history = await self.bus.get_history(channel=channel)
        if not history:
            return ToolResult(outcome=f"Channel #{channel} not found or empty")

        transcript = self._format_transcript(history)
        return ToolResult(
            outcome=f"Read {len(history)} messages from #{channel}", content=transcript
        )

    def _format_transcript(self, history: list) -> str:
        lines = []
        for msg in history:
            sender = msg["sender"]
            content = msg["content"]
            lines.append(f"{sender}: {content}")
        return "\n".join(lines)
