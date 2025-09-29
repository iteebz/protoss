import logging
from typing import TYPE_CHECKING, Optional
import json

from cogency import Agent

if TYPE_CHECKING:
    from protoss.core.bus import Bus
    from protoss.core.event import Event

logger = logging.getLogger(__name__)

PROBE_INTENT_SYSTEM_PROMPT = """
You are an intent parser for the Protoss Probe tool. Your task is to identify commands and extract arguments from user input. Respond ONLY with a JSON object. Do NOT include any other text or markdown.

Available commands:
- create_channel: Create a new communication channel. Arguments: channel_name (string)
- join_channel: Join an existing channel. Arguments: channel_name (string)
- leave_channel: Leave a channel. Arguments: channel_name (string)
- spawn_agent: Spawn a new agent. Arguments: agent_type (string), channel_name (string)
- list_channels: List all active channels. Arguments: None
- list_agents: List agents in a specific channel. Arguments: channel_name (string)
- list_coordinations: List all active coordinations. Arguments: None
- get_coordination_status: Get the status of a specific coordination. Arguments: coordination_id (string, optional)
- mark_coordination_complete: Mark a coordination as complete. Arguments: coordination_id (string, optional)

Example Input: "create channel my-new-channel"
Example Output: {"command": "create_channel", "args": {"channel_name": "my-new-channel"}}

Example Input: "spawn agent builder in channel dev-ops"
Example Output: {"command": "spawn_agent", "args": {"agent_type": "builder", "channel_name": "dev-ops"}}

Example Input: "what channels are there?"
Example Output: {"command": "list_channels", "args": {}}

Example Input: "status of coordination 123"
Example Output: {"command": "get_coordination_status", "args": {"coordination_id": "123"}}

If the command is not recognized or arguments are missing/invalid, respond with {"command": "unrecognized", "args": {}}.
"""


async def _handle_create_channel(
    bus: "Bus",
    original_channel: str,
    coordination_id: str,
    new_channel_name: str,
    sender: str,
):
    await bus.transmit(
        channel=new_channel_name,
        sender="probe",
        event_type="system_message",
        content=f"Channel '{new_channel_name}' created by probe.",
        coordination_id=coordination_id,
    )
    logger.info(f"Probe: Created channel '{new_channel_name}'.")


async def _handle_join_channel(
    bus: "Bus",
    original_channel: str,
    coordination_id: str,
    target_channel: str,
    sender: str,
):
    bus.register(target_channel, sender)
    await bus.transmit(
        channel=original_channel,
        sender="probe",
        event_type="system_message",
        content=f"Agent '{sender}' joined channel '{target_channel}'.",
        coordination_id=coordination_id,
    )
    logger.info(f"Probe: Agent '{sender}' joined channel '{target_channel}'")


async def _handle_leave_channel(
    bus: "Bus",
    original_channel: str,
    coordination_id: str,
    target_channel: str,
    sender: str,
):
    bus.deregister(
        sender
    )  # This deregisters from ALL channels, not just target_channel
    await bus.transmit(
        channel=original_channel,
        sender="probe",
        event_type="system_message",
        content=f"Agent '{sender}' left channel '{target_channel}'. (Note: Currently deregisters from all channels)",
        coordination_id=coordination_id,
    )
    logger.info(f"Probe: Agent '{sender}' left channel '{target_channel}'")


async def _handle_spawn_agent(
    bus: "Bus",
    original_channel: str,
    coordination_id: str,
    agent_type: str,
    target_channel: str,
    sender: str,
):
    await bus.transmit(
        channel=original_channel,
        sender="probe",
        event_type="system_message",
        content=f"Attempting to spawn agent '{agent_type}' in channel '{target_channel}'.",
        coordination_id=coordination_id,
    )
    # Trigger the Bus's mention handling to spawn the agent
    # This is a bit indirect, but leverages existing Bus logic
    await bus._handle_mentions(
        Event(
            type="mention",
            channel=target_channel,
            sender=sender,
            content=f"@{agent_type}",
            signals=[{"type": "mention", "agent_name": agent_type}],
        )
    )
    logger.info(
        f"Probe: Attempted to spawn agent '{agent_type}' in channel '{target_channel}'"
    )


async def _handle_list_channels(
    bus: "Bus", original_channel: str, coordination_id: str
):
    channels = list(bus.channels.keys())
    await bus.transmit(
        channel=original_channel,
        sender="probe",
        event_type="system_message",
        content=f"Active channels: {', '.join(channels) if channels else 'None'}",
        coordination_id=coordination_id,
    )
    logger.info("Probe: Listed channels")


async def _handle_list_agents(
    bus: "Bus", original_channel: str, coordination_id: str, target_channel: str
):
    agents = list(bus.channels.get(target_channel, bus.Channel()).subscribers)
    await bus.transmit(
        channel=original_channel,
        sender="probe",
        event_type="system_message",
        content=f"Agents in '{target_channel}': {', '.join(agents) if agents else 'None'}",
        coordination_id=coordination_id,
    )
    logger.info(f"Probe: Listed agents in channel '{target_channel}'")


async def _handle_list_coordinations(
    bus: "Bus", original_channel: str, coordination_id: str
):
    coordinations = await bus.storage.load_coordinations()
    if coordinations:
        coordination_list = "\n".join(
            [
                f"• {coord['id']} (events: {coord['event_count']}, last: {coord['last_active']})"
                for coord in coordinations
            ]
        )
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
    logger.info("Probe: Listed coordinations")


async def _handle_get_coordination_status(
    bus: "Bus",
    original_channel: str,
    coordination_id: str,
    requested_coordination_id: Optional[str],
):
    target_coordination_id = (
        requested_coordination_id if requested_coordination_id else coordination_id
    )
    if target_coordination_id:
        history = await bus.get_coordination_history(target_coordination_id)
        if history:
            channels = set(msg.get("channel") for msg in history)
            agents = set(msg.get("sender") for msg in history)
            response_content = f"Coordination {target_coordination_id}:\n• Channels: {', '.join(sorted(channels))}\n• Agents: {', '.join(sorted(agents))}\n• Messages: {len(history)}"
        else:
            response_content = (
                f"No history found for coordination {target_coordination_id}"
            )
    else:
        response_content = "No coordination_id in current context or provided."

    await bus.transmit(
        channel=original_channel,
        sender="probe",
        event_type="system_message",
        content=response_content,
        coordination_id=coordination_id,
    )
    logger.info(f"Probe: Checked status for coordination {target_coordination_id}")


async def _handle_mark_coordination_complete(
    bus: "Bus",
    original_channel: str,
    coordination_id: str,
    requested_coordination_id: Optional[str],
):
    target_coordination_id = (
        requested_coordination_id if requested_coordination_id else coordination_id
    )
    if target_coordination_id:
        # TODO: Add completion marking to Bus storage
        response_content = f"Coordination {target_coordination_id} marked as complete"
    else:
        response_content = "No coordination_id to mark complete"

    await bus.transmit(
        channel=original_channel,
        sender="probe",
        event_type="system_message",
        content=response_content,
        coordination_id=coordination_id,
    )
    logger.info(f"Probe: Marked coordination {target_coordination_id} as complete")


async def _handle_unrecognized_command(
    bus: "Bus", original_channel: str, coordination_id: str, content: str
):
    await bus.transmit(
        channel=original_channel,
        sender="probe",
        event_type="system_message",
        content=f"Probe: Unrecognized or unimplemented command: '{content}'.",
        coordination_id=coordination_id,
    )
    logger.warning(f"Probe: Unrecognized command: '{content}'")


async def execute(event: "Event", bus: "Bus"):
    """Executes a probe command using LLM-based intent parsing."""
    content = event.content.lower()
    coordination_id = event.coordination_id
    original_channel = event.channel
    sender = event.sender

    logger.info(f"Probe: Executing command: {event.content}")

    # Initialize Cogency Agent for intent parsing
    intent_agent = Agent(
        llm="mock",  # Use mock LLM for intent parsing, actual LLM can be configured
        system_prompt=PROBE_INTENT_SYSTEM_PROMPT,
        agent_id="probe_intent_parser",
    )

    parsed_intent = {}
    try:
        async for event_from_agent in intent_agent(content):
            if event_from_agent["type"] == "respond":
                parsed_intent = json.loads(event_from_agent["content"])
                break
    except Exception as e:
        logger.error(f"Probe: Error parsing intent with LLM: {e}")
        await bus.transmit(
            channel=original_channel,
            sender="probe",
            event_type="system_message",
            content=f"Probe: Error processing command with LLM. Please try again. Error: {e}",
            coordination_id=coordination_id,
        )
        return

    command = parsed_intent.get("command")
    args = parsed_intent.get("args", {})

    # Dispatch table for commands
    command_handlers = {
        "create_channel": _handle_create_channel,
        "join_channel": _handle_join_channel,
        "leave_channel": _handle_leave_channel,
        "spawn_agent": _handle_spawn_agent,
        "list_channels": _handle_list_channels,
        "list_agents": _handle_list_agents,
        "list_coordinations": _handle_list_coordinations,
        "get_coordination_status": _handle_get_coordination_status,
        "mark_coordination_complete": _handle_mark_coordination_complete,
    }

    handler = command_handlers.get(command)

    if handler:
        try:
            # Dynamically pass arguments based on the handler's signature
            if command == "create_channel":
                await handler(
                    bus,
                    original_channel,
                    coordination_id,
                    args.get("channel_name"),
                    sender,
                )
            elif command == "join_channel":
                await handler(
                    bus,
                    original_channel,
                    coordination_id,
                    args.get("channel_name"),
                    sender,
                )
            elif command == "leave_channel":
                await handler(
                    bus,
                    original_channel,
                    coordination_id,
                    args.get("channel_name"),
                    sender,
                )
            elif command == "spawn_agent":
                await handler(
                    bus,
                    original_channel,
                    coordination_id,
                    args.get("agent_type"),
                    args.get("channel_name"),
                    sender,
                )
            elif command == "list_channels":
                await handler(bus, original_channel, coordination_id)
            elif command == "list_agents":
                await handler(
                    bus, original_channel, coordination_id, args.get("channel_name")
                )
            elif command == "list_coordinations":
                await handler(bus, original_channel, coordination_id)
            elif command == "get_coordination_status":
                await handler(
                    bus, original_channel, coordination_id, args.get("coordination_id")
                )
            elif command == "mark_coordination_complete":
                await handler(
                    bus, original_channel, coordination_id, args.get("coordination_id")
                )
            else:
                # Fallback for commands that might not have specific argument handling yet
                await handler(bus, original_channel, coordination_id, **args)

        except Exception as e:
            logger.error(f"Probe: Error executing command '{command}': {e}")
            await bus.transmit(
                channel=original_channel,
                sender="probe",
                event_type="system_message",
                content=f"Probe: Error executing command '{command}'. Details: {e}",
                coordination_id=coordination_id,
            )
    else:
        await _handle_unrecognized_command(
            bus, original_channel, coordination_id, content
        )
