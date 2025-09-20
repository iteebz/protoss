"""Base class for constitutional AI coordination agents."""

import uuid
import logging
from typing import List, Optional
from ..core.config import Config

logger = logging.getLogger(__name__)


class Unit:
    """Base class for constitutional AI coordination agents."""

    def __init__(self, agent_id: str = None):
        self.id = (
            agent_id or f"{self.__class__.__name__.lower()}-{uuid.uuid4().hex[:8]}"
        )

    @property
    def identity(self) -> str:
        """Constitutional identity for this agent type. Must be overridden by subclasses."""
        raise NotImplementedError(
            f"Unit {self.__class__.__name__} must implement identity property"
        )

    @property
    def tools(self) -> List:
        """Tools available to this agent type. Must be overridden by subclasses."""
        raise NotImplementedError(
            f"Unit {self.__class__.__name__} must implement tools property"
        )

    def _cogency_tools(self, tool_names: List[str]) -> List:
        """Helper to import cogency tools with graceful degradation."""
        try:
            from cogency.tools import TOOLS

            # Filter TOOLS by requested names
            requested_tools = []
            for tool in TOOLS:
                if tool.name in tool_names:
                    requested_tools.append(tool)

            if not requested_tools:
                logger.warning(f"No matching tools found for {tool_names}")

            return requested_tools

        except ImportError:
            logger.warning(
                f"Cogency not available - {self.__class__.__name__} operating with limited capabilities"
            )
            return []

    async def execute(
        self, task: str, channel_context: str, channel_id: str, bus
    ) -> str:
        """Single execution cycle with channel context injection and fresh memory."""

        try:
            identity = self.identity

            if not identity:
                logger.error(f"{self.id} has empty identity property")
                raise ValueError("Constitutional identity cannot be empty")

            logger.debug(f"{self.id} identity length: {len(identity)}")

        except Exception as e:
            logger.error(f"{self.id} failed to access identity/tools: {e}")
            raise

        # Basic implementation - agent analyzes task and provides response
        await bus.transmit(
            channel_id, self.id, f"📋 {self.id} analyzing: {task[:100]}..."
        )

        # Default task processing - subclasses should override for tool execution
        lines = [
            f"Task Analysis: {task}",
            f"Context: {channel_context if channel_context else 'None'}",
            "",
            "Constitutional Response:",
            f"As {self.__class__.__name__}, I have analyzed this task.",
            "Ready for constitutional analysis with available tools.",
            "",
            "[COMPLETE]",  # Emit completion signal
        ]

        result = "\n".join(lines)

        await bus.transmit(
            channel_id, self.id, f"✅ {self.id} completed: {result[:100]}..."
        )
        return result

    async def coordinate(
        self,
        task: str,
        channel_id: str,
        config: Config,
        bus,
        max_cycles: Optional[int] = None,
    ) -> str:
        """Coordination loop - calls execute() until completion signals.

        Args:
            task: The meta-task to coordinate on
            channel_id: Channel for team coordination
            config: Configuration object containing coordination parameters
            bus: Bus instance for coordination
            max_cycles: Maximum coordination cycles before giving up (uses config default if None)

        Returns:
            Completion status message

        Raises:
            ValueError: If task or channel_id is empty
        """
        if not task:
            raise ValueError("Task cannot be empty")
        if not channel_id:
            raise ValueError("Channel ID cannot be empty")

        from ..core.coordination import flatten, parse

        if max_cycles is None:
            max_cycles = config.max_cycles

        logger.info(f"{self.id} starting coordination on {channel_id}")
        logger.debug(f"Task: {task}")

        # Ensure live routing knows this unit is present
        bus.register(channel_id, self.id)

        cycle = 0
        while cycle < max_cycles:
            cycle += 1
            logger.debug(f"{self.id} starting cycle {cycle}")

            # Get channel context and flatten for agent
            recent_messages = bus.get_history(channel_id)
            channel_context = flatten(recent_messages, config)

            try:
                # Single execution cycle - pass actual task and context separately
                response = await self.execute(task, channel_context, channel_id, bus)

                # Parse completion signals
                signals = parse(response, config)

                if signals.complete:
                    logger.info(f"{self.id} completed task in cycle {cycle}")
                    return f"Task completed by {self.id} in {cycle} cycles"
                elif signals.escalate:
                    logger.info(f"{self.id} escalating in cycle {cycle}")
                    # Import here to avoid circular dependency
                    from ..agents.conclave import Conclave
                    from ..core.deliberation import consult

                    consultation = await consult(
                        f"Agent escalation from {self.id}: {response}",
                        bus=bus,
                        conclave=lambda perspective, unit_id: Conclave(
                            perspective, unit_id
                        ),
                    )
                    await bus.transmit(channel_id, "conclave", consultation)
                    return f"Task escalated for constitutional consultation in cycle {cycle}"

                logger.debug(
                    f"{self.id} cycle {cycle} complete, continuing coordination"
                )

            except Exception as e:
                logger.warning(f"{self.id} cycle {cycle} failed: {e}")
                if not config.retry:
                    raise
                # Continue to next cycle - fault tolerance
                continue

        logger.warning(
            f"{self.id} reached max cycles ({max_cycles}) without completion"
        )
        return f"{self.id} reached maximum cycles ({max_cycles}) without completion"

    def get_history(self, channel: str, since_timestamp: float = 0, bus=None) -> List:
        """Get channel message history - requires bus instance."""
        if bus is None:
            raise ValueError("Bus instance required for coordination")
        return bus.get_history(channel, since_timestamp)
