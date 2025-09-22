import logging
import re
import uuid

# This agent is not an LLM-driven Unit. It is a deterministic, heuristic agent.
# It requires a direct connection to the system Bus to perform its duties.
# We are assuming the bus_connection object will have the following methods:
# - create_channel(channel_id: str)
# - broadcast(message: str, channel: str)

logger = logging.getLogger(__name__)


class Probe:
    """
    A Heuristic Agent that acts as a function library for the swarm.

    As per the canonical doctrine in `emergence.md`, the Probe performs
    deterministic infrastructure tasks. It is not an LLM-driven agent.
    It is ephemeral, executing a single command before despawning.
    """

    def __init__(self, bus_connection):
        """
        Initializes the Probe with a connection to the system Bus.

        Args:
            bus_connection: An object providing an interface to the Bus.
        """
        self.bus = bus_connection
        self.id = f"probe-{uuid.uuid4().hex[:8]}"
        logger.info(f"Probe {self.id} has been spawned.")

    async def execute(self, summoning_message: str):
        """
        The single entry point for the Probe. It parses the summoning
        message and executes the requested infrastructure function.
        """
        logger.debug(f"{self.id} executing command from message: '{summoning_message}'")

        # --- Channel Creation ---
        create_channel_pattern = re.compile(
            r"create.*?channel for '(.+?)'(?: and then instruct '(.+?)')?",
            re.IGNORECASE,
        )
        create_channel_match = create_channel_pattern.search(summoning_message)

        if create_channel_match:
            description, next_instruction = create_channel_match.groups()
            await self._handle_channel_creation(description, next_instruction)
            await self.bus.broadcast(message="!despawn", sender=self.id)
            logger.info(f"Probe {self.id} has completed its task and despawned.")
            return

        # --- Provide Channel History ---
        get_history_pattern = re.compile(
            r"provide (the full )?channel history for (\S+)", re.IGNORECASE
        )
        get_history_match = get_history_pattern.search(summoning_message)

        if get_history_match:
            requested_channel_id = get_history_match.group(2)
            await self._handle_history_request(requested_channel_id)
            await self.bus.broadcast(message="!despawn", sender=self.id)
            logger.info(f"Probe {self.id} has completed its task and despawned.")
            return

        logger.warning(
            f"{self.id} could not parse a valid command from: '{summoning_message}'"
        )
        await self.bus.broadcast(message="!despawn", sender=self.id)
        logger.info(f"Probe {self.id} has completed its task and despawned.")

    async def _handle_channel_creation(
        self, description: str, next_instruction: str | None
    ):
        """
        Handles the logic for channel creation and optional instruction delivery.
        """
        # Create a URL-friendly slug from the description for the channel name.
        channel_slug = re.sub(r"[\s_]+", "-", description.lower()).strip("-")
        new_channel_id = f"task:{channel_slug}:{uuid.uuid4().hex[:8]}:active"

        try:
            self.bus.create_channel(new_channel_id)
            logger.info(f"{self.id} successfully created channel: {new_channel_id}")

            if next_instruction:
                # Fulfilling its role as the Herald, the Probe delivers the first
                # command to the newly created channel.
                await self.bus.broadcast(
                    message=next_instruction, channel=new_channel_id
                )
                logger.info(
                    f"{self.id} delivered herald instruction to {new_channel_id}: '{next_instruction}'"
                )

        except Exception as e:
            # If channel creation fails, log the error. The Probe will still despawn.
            logger.error(
                f"{self.id} failed during channel creation or instruction delivery for {new_channel_id}: {e}"
            )

    async def _handle_history_request(self, requested_channel_id: str):
        """
        Handles the logic for providing channel history.
        """
        try:
            # This assumes self.bus has a history method.
            channel_history_messages = await self.bus.history(requested_channel_id)
            channel_history = "\n".join(
                [f"{msg.sender}: {msg.content}" for msg in channel_history_messages]
            )
            await self.bus.broadcast(
                message=f"Probe: Here is the requested history for {requested_channel_id}:\n{channel_history}",
                channel=requested_channel_id,
                sender=self.id,
            )
            logger.info(
                f"{self.id} successfully provided history for {requested_channel_id}"
            )

        except Exception as e:
            logger.error(
                f"{self.id} failed during history request for {requested_channel_id}: {e}"
            )
            await self.bus.broadcast(
                message=f"Probe: Error retrieving history for {requested_channel_id}: {e}",
                channel=requested_channel_id,
                sender=self.id,
            )
