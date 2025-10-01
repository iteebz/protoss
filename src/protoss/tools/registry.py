from cogency.tools import tools


def protoss_tools(bus=None, protoss=None, parent_channel=None):
    """Get all tools including Protoss channel coordination."""
    from .channel import ChannelList, ChannelRead, ChannelSpawn

    base_tools = tools()

    if not bus:
        return base_tools

    channel_tools = [
        ChannelList(bus=bus),
        ChannelRead(bus=bus),
        ChannelSpawn(bus=bus, protoss=protoss, parent_channel=parent_channel),
    ]

    return base_tools + channel_tools
