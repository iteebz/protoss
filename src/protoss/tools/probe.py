import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protoss.core.bus import Bus
    from protoss.core.event import Event

logger = logging.getLogger(__name__)


async def execute(event: "Event", bus: "Bus"):
    """Executes a probe command as a direct function call."""
    content = event.content.lower()
    coordination_id = event.coordination_id
    original_channel = event.channel

    logger.info(f"Probe: Executing command: {event.content}")

    # Command: Create a channel
    match_create_channel = re.search(r"create a channel for '([^']+)'", content)
    if match_create_channel:
        new_channel_name = match_create_channel.group(1)
        await bus.transmit(
            channel=new_channel_name,
            sender="probe",
            event_type="system_message",
            content=f"Channel '{new_channel_name}' created by probe.",
            coordination_id=coordination_id,
        )
        logger.info(f"Probe: Created channel '{new_channel_name}'.")

        # Check for instruction to an agent in the new channel
        match_instruct_agent = re.search(
            r"and then instruct '@([^']+)' to begin work'", content
        )
        if match_instruct_agent:
            target_agent = match_instruct_agent.group(1)
            instruction_content = (
                f"@{target_agent} begin work in channel '{new_channel_name}'."
            )
            await bus.transmit(
                channel=new_channel_name,
                sender="probe",
                event_type="agent_message",
                content=instruction_content,
                coordination_id=coordination_id,
            )
            logger.info(f"Probe: Instructed @{target_agent} in '{new_channel_name}'.")

    # Command: List active coordinations
    elif "list coordinations" in content or "list active" in content:
        coordinations = await bus.storage.load_coordinations()
        if coordinations:
            coordination_list = "\n".join([
                f"• {coord['id']} (events: {coord['event_count']}, last: {coord['last_active']})"
                for coord in coordinations
            ])
            response_content = f"Active coordinations:\n{coordination_list}"
        else:
            response_content = "No active coordinations found."
        
        await bus.transmit(
            channel=original_channel,
            sender="probe",
            event_type="system_message",
            content=response_content,
            coordination_id=coordination_id,
        )
        return

    # Command: Check coordination status
    elif "status" in content:
        if coordination_id:
            history = await bus.get_coordination_history(coordination_id)
            if history:
                channels = set(msg.get("channel") for msg in history)
                agents = set(msg.get("sender") for msg in history)
                response_content = f"Coordination {coordination_id}:\n• Channels: {', '.join(sorted(channels))}\n• Agents: {', '.join(sorted(agents))}\n• Messages: {len(history)}"
            else:
                response_content = f"No history found for coordination {coordination_id}"
        else:
            response_content = "No coordination_id in current context"
            
        await bus.transmit(
            channel=original_channel,
            sender="probe",
            event_type="system_message",
            content=response_content,
            coordination_id=coordination_id,
        )
        return

    # Command: Mark coordination complete
    elif "complete" in content or "mark complete" in content:
        if coordination_id:
            # TODO: Add completion marking to Bus storage
            response_content = f"Coordination {coordination_id} marked as complete"
        else:
            response_content = "No coordination_id to mark complete"
            
        await bus.transmit(
            channel=original_channel,
            sender="probe",
            event_type="system_message",
            content=response_content,
            coordination_id=coordination_id,
        )
        return

    # Respond to the original channel to confirm execution
    await bus.transmit(
        channel=original_channel,
        sender="probe",
        event_type="system_message",
        content=f"Probe command executed: {event.content}",
        coordination_id=coordination_id,
    )
