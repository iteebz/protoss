"""Spawn context and topology helpers."""


async def build_spawn_context(storage, current_channel: str) -> str:
    """Build spawn context with active channel topology."""
    channels = await storage.get_channels()

    if not channels:
        channels = [current_channel]

    channel_list = ", ".join([f"#{ch}" for ch in sorted(channels)])

    return f"""[Active channels: {channel_list}]
[You are in: #{current_channel}]"""
