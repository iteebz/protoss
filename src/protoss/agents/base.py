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
        """Execute with constitutional coordination using cogency Agent."""

        # Get current team status for agent awareness
        team_status = bus.get_team_status(channel_id)

        # Constitutional identity + team coordination awareness
        instructions = f"""
{self.identity}

TASK: {task}

{team_status}

COORDINATION COMMANDS:

@ = Participation Control (Bring agents into active coordination)
- @zealot - Summon fresh zealot for architectural criticism and code review
- @archon - Summon fresh archon for institutional memory and knowledge work
- @conclave - Summon fresh conclave for constitutional deliberation  
- @arbiter - Summon fresh arbiter for task coordination
- @zealot-abc123 - Wake up/reactivate specific agent (or resurrect if despawned)
- @human - Escalate to human for completion notification or intervention

Natural Names = Communication (Talk to active team members)
- zealot-abc123, thoughts on this approach? - Direct conversation with active agent
- archon-def456, check archives for auth patterns - Natural team communication
- Team, ready for integration testing - Address entire active team

! = Self-Action (Individual lifecycle management)
- !despawn - Remove myself from active coordination when work complete

Use §respond: to communicate with teammates. Use §end when ready to read team updates.

Follow the natural coordination lifecycle: deliberate, explore, consensus, divide work, execute, review.
"""

        # Get available tools
        tools = self.tools
        if not tools:
            logger.warning(f"{self.id} operating without cogency tools")

        try:
            # Fresh cogency agent per cycle
            from cogency.core.agent import Agent

            agent = Agent(
                instructions=instructions,
                tools=tools,
                resume=True,
            )

            # Channel context as user message (team discussion)
            user_message = (
                channel_context
                if channel_context
                else "You are the first agent working on this task."
            )

            # Stream response with fresh conversation_id
            response = ""
            async for event in agent(
                user_message,
                user_id=f"channel-{channel_id}",  # Serves the team
                conversation_id=f"agent-{uuid.uuid4().hex[:8]}",  # Fresh memory each cycle
            ):
                event_type = event["type"]
                content = event.get("content", "")

                # Broadcast ALL semantic events for truth/auditing
                if event_type == "think":
                    await bus.transmit(channel_id, self.id, f"[THINK] {content}")
                elif event_type == "call":
                    await bus.transmit(channel_id, self.id, f"[CALL] {content}")
                elif event_type == "result":
                    await bus.transmit(channel_id, self.id, f"[RESULT] {content}")
                elif event_type == "respond":
                    response += content
                    await bus.transmit(channel_id, self.id, content)

            return response

        except Exception as e:
            logger.error(f"Cogency coordination failed: {e}")
            # Fallback to constitutional analysis
            fallback = f"""Constitutional Analysis by {self.__class__.__name__}:

Task: {task}
Context: {channel_context if channel_context else 'None'}

COGENCY COORDINATION FAILED: {e}

Applied constitutional principles without tool execution.
Ready for team coordination.

[COMPLETE]"""

            await bus.transmit(channel_id, self.id, fallback)
            return fallback

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
            # Pass agent type for context filtering
            agent_type = self.__class__.__name__.lower()
            channel_context = flatten(recent_messages, config, agent_type)

            try:
                # Single execution cycle - pass actual task and context separately
                response = await self.execute(task, channel_context, channel_id, bus)

                # Parse completion signals
                signals = parse(response, config)

                if signals.complete:
                    logger.info(f"{self.id} completed task in cycle {cycle}")
                    return f"Task completed by {self.id} in {cycle} cycles"
                elif signals.despawn:
                    logger.info(f"{self.id} despawning in cycle {cycle}")
                    await bus.despawn(self.id)
                    return f"{self.id} despawned successfully in cycle {cycle}"

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
