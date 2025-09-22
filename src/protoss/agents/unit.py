import asyncio
import json
import logging
import uuid
import websockets
from typing import List, Optional, Tuple
from ..constitution import SWARM_CONSTITUTION, COORDINATION_PATTERNS

logger = logging.getLogger(__name__)


class Unit:
    """Base class for constitutional AI coordination agents."""

    def __init__(self, agent_id: str = None, max_cycles: int = 100):
        self.id = (
            agent_id or f"{self.__class__.__name__.lower()}-{uuid.uuid4().hex[:8]}"
        )
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.max_cycles = max_cycles

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

            requested_tools = [tool for tool in TOOLS if tool.name in tool_names]
            if not requested_tools:
                logger.warning(f"No matching tools found for {tool_names}")
            return requested_tools
        except ImportError:
            logger.warning(
                f"Cogency not available - {self.__class__.__name__} operating with limited capabilities"
            )
            return []

    def _get_instructions(self, task: str, team_status: str) -> str:
        """Build layered constitutional instruction stack."""
        return f"""\
{SWARM_CONSTITUTION}

{self.identity}

## CURRENT TASK
{task}

## COORDINATION CONTEXT
{team_status}

{COORDINATION_PATTERNS}
"""

    async def _transmit(self, msg_type: str, channel: str, content: Optional[dict] = None):
        """Sends a structured message to the Bus via WebSocket."""
        if not self.websocket or self.websocket.state != websockets.protocol.State.OPEN:
            logger.error("WebSocket is not connected or not open. Cannot transmit message.")
            return

        message = {"type": msg_type, "channel": channel}
        if content:
            message.update(content)

        await self.websocket.send(json.dumps(message))

    async def execute(
        self, task: str, channel_context: str, channel_id: str, team_status: str
    ) -> dict:
        """Execute a single cycle of constitutional coordination.
        
        Returns a dictionary containing the response and a signal for the coordinator.
        """
        instructions = self._get_instructions(task, team_status)
        tools = self.tools
        if not tools:
            logger.warning(f"{self.id} operating without cogency tools")

        try:
            from cogency.core.agent import Agent

            agent = Agent(instructions=instructions, tools=tools)
            user_message = channel_context or "You are the first agent on this task."

            response_text = ""
            async for event in agent(
                user_message,
                user_id=f"channel-{channel_id}",
                conversation_id=f"agent-{uuid.uuid4().hex[:8]}",
            ):
                event_type = event["type"]
                content = event.get("content", "")
                logger.debug(f"Cogency event: {event}")

                if event_type == "think":
                    await self._transmit("msg", channel_id, {"content": f"[THINK] {content}"})
                elif event_type == "call":
                    await self._transmit("msg", channel_id, {"content": f"[CALL] {content}"})
                elif event_type == "result":
                    await self._transmit("msg", channel_id, {"content": f"[RESULT] {content}"})
                elif event_type == "respond":
                    response_text += content
                    await self._transmit("msg", channel_id, {"content": content})
            
            # Determine signal from the final response
            signal = "continue"
            if "!despawn" in response_text:
                signal = "despawn"
            elif "!complete" in response_text:
                signal = "complete"

            return {"response": response_text, "signal": signal}

        except ImportError: # Cogency not available
            logger.warning(f"Cogency not available for {self.id}. Checking task for direct signals.")
            if "!despawn" in task:
                return {"response": "Despawning as requested by task due to Cogency unavailability.", "signal": "despawn"}
            elif "!complete" in task:
                return {"response": "Completing as requested by task due to Cogency unavailability.", "signal": "complete"}
            else:
                return {"response": "Continuing without Cogency.", "signal": "continue"}
        except Exception as e:
            logger.error(f"Cogency coordination failed: {e}")
            fallback = f"Constitutional Analysis by {self.__class__.__name__}: COGENCY FAILED: {e}."
            await self._transmit("msg", channel_id, {"content": fallback})
            signal = "despawn" if "!despawn" in task else "continue" # Default to continue if not explicitly despawn
            return {"response": fallback, "signal": signal}

    async def _synchronize(self, channel_id: str) -> Tuple[str, str]:
        """Synchronize with the swarm by fetching channel history and team status."""
        await self._transmit("history_req", channel_id)
        await self._transmit("status_req", channel_id)

        history_str = ""
        status_str = "Team status currently unavailable."
        responses_received = 0

        try:
            async with asyncio.timeout(5.0):
                while responses_received < 2:
                    raw_response = await self.websocket.recv()
                    data = json.loads(raw_response)

                    if data.get("channel") != channel_id:
                        continue  # Ignore messages from other channels

                    msg_type = data.get("type")
                    if msg_type == "history_resp":
                        history_str = "\n".join(data.get("history", []))
                        responses_received += 1
                    elif msg_type == "status_resp":
                        status_str = data.get("status", "")
                        responses_received += 1
                    else:
                        logger.debug(f"Ignoring message of type {msg_type} during sync.")
        except (asyncio.TimeoutError, json.JSONDecodeError) as e:
            logger.warning(f"Did not receive full context from bus for {channel_id}: {e}")

        return history_str, status_str

    async def coordinate(
        self,
        task: str,
        channel_id: str,
        bus_url: str,
        max_cycles: int = 100,
    ) -> str:
        """Autonomous coordination loop for the agent.

        Connects to the bus and executes coordination cycles until the task is
        complete, the agent despawns, or the max cycle limit is reached.
        """
        if not all([task, channel_id, bus_url]):
            raise ValueError("Task, Channel ID, and Bus URL cannot be empty")

        uri = f"{bus_url}/{self.id}"

        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                logger.info(f"{self.id} connected to Bus at {bus_url}")
                await self._transmit("join_channel", channel_id)

                cycle = 0
                while cycle < max_cycles:
                    cycle += 1
                    logger.debug(f"{self.id} starting cycle {cycle}")

                    channel_context, team_status = await self._synchronize(channel_id)

                    try:
                        # The execute method will now return a dictionary with 'response' and 'signal'
                        execution_result = await self.execute(
                            task, channel_context, channel_id, team_status
                        )
                        
                        signal = execution_result.get("signal", "continue")

                        if signal == "complete":
                            logger.info(f"{self.id} completed task in {cycle} cycles")
                            await self._transmit("leave_channel", channel_id, {"reason": "complete"})
                            if self.websocket and self.websocket.state == websockets.protocol.State.OPEN:
                                await self.websocket.close()
                            return f"Task completed by {self.id}"
                        elif signal == "despawn":
                            logger.info(f"{self.id} despawning in cycle {cycle}")
                            await self._transmit("leave_channel", channel_id, {"reason": "despawn"})
                            if self.websocket and self.websocket.open:
                                await self.websocket.close()
                            return f"{self.id} despawned successfully"

                    except Exception as e:
                        logger.error(f"{self.id} cycle {cycle} failed: {e}")
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
            logger.error(f"{self.id} failed to connect to Bus: {e}")
            return f"{self.id} connection to Bus failed"
        finally:
            self.websocket = None


