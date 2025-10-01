"Constitutional agent with pure conversation coordination."

import asyncio
import logging
import time

try:
    import cogency
    from cogency.lib.llms.openai import OpenAI
except ImportError:
    cogency = None

from .bus import Bus
from ..constitution import CONSTITUTIONS, GUIDELINES
from ..tools import protoss_tools

logger = logging.getLogger(__name__)


class Agent:
    """Agent that coordinates through conversation."""

    def __init__(
        self,
        agent_type: str,
        bus: Bus,
        channel: str = "human",
        base_dir: str = None,
        protoss=None,
    ):
        self.agent_type = agent_type
        self.bus = bus
        self.channel = channel
        self.conversation_id = channel  # Use channel as conversation_id
        self.running = True
        self.last_poll_time: float = 0  # Track when we last read messages
        self.base_dir = base_dir
        self.errors = []  # Collect tool errors for debugging

        # Load constitutional identity and coordination guidelines separately
        constitutional_identity = self._load_constitutional_identity()
        coordination_guidelines = self._load_coordination_guidelines()

        # Build tool list with channel coordination
        all_tools = protoss_tools(
            bus=self.bus, protoss=protoss, parent_channel=self.channel
        )

        # Initialize cogency for reasoning with default tools and shared sandbox
        self.cogency_agent = (
            cogency.Agent(
                llm=OpenAI(http_model="gpt-4.1-mini"),
                identity=constitutional_identity,  # Strong constitutional identity
                instructions=coordination_guidelines,  # Team coordination context
                tools=all_tools,
                base_dir=self.base_dir,  # Shared sandbox for coordination
                mode="replay",
                profile=False,
                history_window=200,
            )
            if cogency
            else None
        )

    def _load_constitutional_identity(self) -> str:
        """Load constitutional identity from the registry."""
        return CONSTITUTIONS.get(
            self.agent_type,
            f"You are {self.agent_type}, a software development agent.",
        )

    def _load_coordination_guidelines(self) -> str:
        """Load coordination guidelines."""
        return GUIDELINES

    async def run(self):
        """Main coordination loop - initial context + diff updates."""
        logger.info(f"Agent {self.agent_type} starting in #{self.channel}")

        # Initial context assembly - get full channel history
        await self._initial_context_load()

        # Coordination loop - process only new messages
        while self.running:
            try:
                # Set the poll time BEFORE we get history and start processing
                poll_time = time.time()
                new_messages = await self.bus.get_history(
                    channel=self.channel, since=self.last_poll_time
                )
                self.last_poll_time = poll_time

                if new_messages and self.cogency_agent:
                    # Filter out our own messages from the batch
                    filtered_messages = [
                        msg for msg in new_messages if msg["sender"] != self.agent_type
                    ]

                    if filtered_messages:
                        conversation = self._format_history(filtered_messages)
                        context = conversation
                        await self._process_with_cogency(context)

                # Check if we should continue
                if not self.running:
                    break

                # Coordination heartbeat - pause before next cycle
                await asyncio.sleep(2.0)

            except Exception as e:
                logger.error(f"Agent {self.agent_type} coordination error: {e}")
                break

        logger.info(f"Agent {self.agent_type} stopping")

    async def _initial_context_load(self):
        """Load full channel history on agent spawn."""
        history = await self.bus.get_history(self.channel)

        if history and self.cogency_agent:
            # Format full conversation for initial context
            context = self._format_history(history)
            logger.info(
                f"Agent {self.agent_type} loading initial context: {len(history)} messages"
            )

            # Process full history as initial context
            await self._process_with_cogency(f"Channel history:\n{context}")

        # Set poll time to now - future polls will only get diffs
        self.last_poll_time = time.time()

    def _format_history(self, history) -> str:
        """Format message history for context."""
        return "\n".join([f"{msg['sender']}: {msg['content']}" for msg in history])

    async def _process_with_cogency(self, content: str):
        """Process content through cogency and respond, with self-correction."""
        if not self.cogency_agent:
            logger.warning(f"Agent {self.agent_type} has no cogency agent")
            return

        try:
            async for event in self.cogency_agent(
                content, user_id=self.agent_type, conversation_id=self.conversation_id
            ):
                if event["type"] == "respond":
                    response = event["content"]
                    timestamp = time.strftime("%H:%M:%S")
                    logger.info(
                        f"\n--- {self.agent_type.upper()} [{timestamp}] ---\n{response}\n"
                    )
                    await self.bus.send(self.agent_type, response, self.channel)

                    # Check for exit signals
                    if "!despawn" in response.lower():
                        logger.info(f"Agent {self.agent_type} despawning")
                        self.running = False
                        break

                    if "!complete" in response.lower():
                        logger.info(f"Agent {self.agent_type} signaling task complete")
                        
                        # Broadcast completion to parent channel if exists
                        parent = await self.bus.storage.get_parent_channel(self.channel)
                        if parent:
                            await self.bus.send(
                                "system",
                                f"← #{self.channel}: {self.agent_type} - {response}",
                                parent
                            )
                        
                        # Don't despawn on !complete - let other agents see it and decide

                elif event["type"] == "result":
                    payload = event.get("payload", {})
                    outcome = payload.get("outcome", "")
                    call = payload.get("call", {})
                    tool_name = call.get("name", "") if isinstance(call, dict) else ""

                    # Broadcast file operations and channel spawns
                    if tool_name in ("file_write", "file_edit"):
                        if (
                            "error" not in outcome.lower()
                            and "failed" not in outcome.lower()
                        ):
                            await self.bus.send(
                                self.agent_type, f"✓ {outcome}", self.channel
                            )
                    
                    if tool_name == "channel_spawn":
                        if (
                            "error" not in outcome.lower()
                            and "failed" not in outcome.lower()
                        ):
                            await self.bus.send(
                                self.agent_type, f"→ {outcome}", self.channel
                            )

                    # Log errors (no broadcast - agent handles communication)
                    if (
                        "error" in outcome.lower()
                        or "failed" in outcome.lower()
                        or "invalid" in outcome.lower()
                    ):
                        error_record = {
                            "agent": self.agent_type,
                            "tool": tool_name,
                            "call": call,
                            "outcome": outcome,
                        }
                        self.errors.append(error_record)
                        logger.warning(
                            f"{self.agent_type} tool error: {tool_name} - {outcome}"
                        )

                elif event["type"] == "end":
                    # §end breaks the reasoning cycle - return to diff polling
                    break
        except Exception as e:
            error_message = f"A tool error occurred during my last action: {e}. I must analyze this error, inform my teammates, and correct my plan."
            logger.error(
                f"Agent {self.agent_type} stream error: {e}. Attempting self-correction."
            )
            # Log the full exception details for diagnosis
            logger.exception(
                f"Detailed error during agent {self.agent_type} stream processing."
            )
            # Feed the error back into the reasoning loop
            await self._process_with_cogency(error_message)
