import asyncio
import json
import logging
import websockets
import argparse
from typing import List, Optional, Dict
from ..constitution import SWARM_CONSTITUTION, COORDINATION_PATTERNS
from ..core.config import Config
import time

logger = logging.getLogger(__name__)


class Unit:
    """Pure constitutional AI coordination agent interface."""

    def __init__(self, agent_id: str, agent_type: str, channel_id: str, config: Config):
        self.id = agent_id
        self.agent_type = agent_type
        self.channel_id = channel_id
        self.config = config
        self._websocket = None  # Agent's own websocket for receiving

    async def _connect_websocket(self):
        """Establishes a websocket connection to the Bus for receiving messages."""
        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            return
        try:
            uri = f"{self.config.bus_url}/agent/{self.id}"
            self._websocket = await websockets.connect(uri)
            logger.info(f"{self.id} connected to Bus at {uri}")
        except Exception as e:
            logger.error(f"{self.id} failed to connect to Bus: {e}")
            self._websocket = None

    async def _receive_message(self, timeout: int = 1) -> Optional[Dict]:
        """Receives and parses a single message from the websocket with a timeout."""
        try:
            if (
                not self._websocket
                or self._websocket.state != websockets.protocol.State.OPEN
            ):
                # If websocket is not open, it means poll_channel_for_response didn't connect it.
                # Raise an error or return None, as _receive_message should not attempt to connect.
                logger.warning(
                    f"{self.id} _receive_message called with closed websocket."
                )
                return None

            message_str = await asyncio.wait_for(
                self._websocket.recv(), timeout=timeout
            )
            message = json.loads(message_str)
            return message
        except asyncio.TimeoutError:
            return None
        except websockets.exceptions.ConnectionClosedOK:
            logger.info(f"{self.id} websocket connection closed.")
            self._websocket = None
            return None
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            self._websocket = None
            return None

    async def poll_channel_for_response(
        self,
        timeout: int = 10,
        sender_filter: Optional[str] = None,
        content_filter: Optional[str] = None,
        signal_type_filter: Optional[type] = None,
    ) -> Optional[Dict]:
        """Polls the channel for a message that matches the given filters.

        Args:
            timeout: How long to poll for a message (in seconds).
            sender_filter: If provided, only messages from this sender will be returned.
            content_filter: If provided, only messages containing this substring will be returned.
            signal_type_filter: If provided, only messages containing this signal type will be returned.

        Returns:
            The parsed message dictionary if a match is found, otherwise None.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            message = await self._receive_message(
                timeout=1
            )  # Short timeout for polling
            if message is None:
                continue

            # Apply filters
            if sender_filter and message.get("sender") != sender_filter:
                continue
            if content_filter and content_filter not in message.get("content", ""):
                continue

            # For signal_type_filter, we need to parse signals from the content
            if signal_type_filter:
                signals = parser.parse_signals(message.get("content", ""))
                if not any(isinstance(s, signal_type_filter) for s in signals):
                    continue

            logger.debug(f"{self.id} received matching message: {message}")
            return message
        logger.info(f"{self.id} timed out polling for message.")
        return None

    @property
    def identity(self) -> str:
        """Pure constitutional identity from constitution/ namespace. Override this."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement identity")

    @property
    def tools(self) -> List:
        """Constitutional tools. Override if needed."""
        return []

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

    async def _connect_to_bus(self):
        """Establish WebSocket connection to the Bus."""
        uri = f"{self.config.bus_url}/{self.agent_id}"
        try:
            self._websocket = await websockets.connect(uri)
            logger.info(f"{self.agent_id} connected to Bus at {self.config.bus_url}")
            # Register with the bus
            await self._websocket.send(
                json.dumps({"type": "join_channel", "channel": self.channel_id})
            )
        except Exception as e:
            logger.error(f"{self.agent_id} failed to connect to Bus: {e}")
            self._websocket = None

    async def _disconnect_from_bus(self):
        """Close WebSocket connection to the Bus."""
        if self._websocket and (
            self._websocket.state == websockets.protocol.State.OPEN
        ):
            await self._websocket.close()
            logger.info(f"{self.agent_id} disconnected from Bus.")
        self._websocket = None

    async def __call__(self, context: str) -> str:
        """Pure constitutional function: context → constitutional response."""
        instructions = f"""\
{SWARM_CONSTITUTION}

{self.identity}

## CONSTITUTIONAL CONTEXT
{context}

{COORDINATION_PATTERNS}
"""
        try:
            from cogency.core.agent import Agent

            agent = Agent(instructions=instructions, tools=self.tools)
            response_text = ""

            async for event in agent(
                "Apply your constitutional perspective to this context."
            ):
                if event["type"] == "respond":
                    response_text += event.get("content", "")

            return response_text

        except ImportError:
            return f"Constitutional reasoning unavailable: {self.__class__.__name__} perspective needed but Cogency not available."

    async def broadcast(self, response: str):
        """Pure broadcast layer - response only."""
        if not self._websocket or not (
            self._websocket.state == websockets.protocol.State.OPEN
        ):
            logger.warning(
                f"{self.agent_id} websocket not open, cannot broadcast message."
            )
            return

        message = {
            "type": "msg",
            "channel": self.channel_id,
            "content": response,
            "sender": self.agent_id,
        }
        try:
            await self._websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

    async def coordinate(self, task: str) -> str:
        """Pure constitutional coordination."""
        from cogency.core.agent import Agent

        instructions = f"""\
{SWARM_CONSTITUTION}

{self.identity}

{COORDINATION_PATTERNS}
"""

        agent = Agent(instructions=instructions, tools=self.tools)

        response_text = ""
        async for event in agent(task):
            if event["type"] == "respond":
                response_text += event.get("content", "")

        await self.broadcast(response_text)

        # Return completion signal if present
        if "!complete" in response_text:
            return "complete"
        elif "!despawn" in response_text:
            return "despawn"
        return "continue"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Protoss Unit agent.")
    parser.add_argument("--agent-id", required=True, help="Unique ID for the agent.")
    parser.add_argument(
        "--agent-type", required=True, help="Type of the agent (e.g., zealot, archon)."
    )
    parser.add_argument("--channel", required=True, help="Channel ID for coordination.")
    parser.add_argument("--bus-url", required=True, help="URL of the Protoss Bus.")
    parser.add_argument("--task", required=True, help="The task context for the agent.")
    parser.add_argument(
        "--params",
        default="{}",
        help="JSON string of extra params for agent constructor.",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    async def main():
        from .zealot import Zealot
        from .archon import Archon
        from .arbiter import Arbiter
        from .conclave import Conclave

        agent_classes = {
            "zealot": Zealot,
            "archon": Archon,
            "arbiter": Arbiter,
            "conclave": Conclave,
        }

        agent_class = agent_classes.get(args.agent_type)
        if not agent_class:
            logger.error(f"Unknown agent type: {args.agent_type}")
            return

        config = Config().with_overrides(bus_url=args.bus_url)

        # Prepare constructor arguments
        constructor_args = {
            "agent_id": args.agent_id,
            "agent_type": args.agent_type,
            "channel_id": args.channel,
            "config": config,
        }

        # Add extra parameters from the command line
        try:
            extra_params = json.loads(args.params)
            constructor_args.update(extra_params)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in --params: {args.params}")
            return

        # Create agent instance with all arguments
        agent_instance = agent_class(**constructor_args)

        await agent_instance._connect_to_bus()
        try:
            action = extra_params.get("action")
            if action == "seed_channel":
                logger.info(f"{agent_instance.agent_id} seeding channel {args.channel}")
                result = await agent_instance.seed_channel(args.task, args.channel)
                await agent_instance.broadcast(result)
            elif action == "respond_to_mention":
                logger.info(
                    f"{agent_instance.agent_id} responding to mention in {args.channel}"
                )
                result = await agent_instance.respond_to_mention(
                    args.task, args.channel
                )
                await agent_instance.broadcast(result)
            elif action == "archive_for_review":
                logger.info(
                    f"{agent_instance.agent_id} archiving for review in {args.channel}"
                )
                result = await agent_instance.archive_for_review(
                    args.task
                )  # args.task is the content to archive
                await agent_instance.broadcast(result)
            elif action == "get_artifact":
                review_id = extra_params.get("review_id")
                if not review_id:
                    logger.error("get_artifact action requires 'review_id' in params.")
                    return
                logger.info(f"{agent_instance.agent_id} getting artifact {review_id}")
                result = await agent_instance.get_artifact(review_id)
                await agent_instance.broadcast(result or "Artifact not found.")
            elif action == "get_summary":
                review_id = extra_params.get("review_id")
                if not review_id:
                    logger.error("get_summary action requires 'review_id' in params.")
                    return
                logger.info(
                    f"{agent_instance.agent_id} getting summary for {review_id}"
                )
                result = await agent_instance.get_summary(review_id)
                await agent_instance.broadcast(result or "Summary not found.")
            elif action == "perform_review":
                review_id = extra_params.get("review_id")
                if not review_id:
                    logger.error(
                        "perform_review action requires 'review_id' in params."
                    )
                    return
                logger.info(
                    f"{agent_instance.agent_id} performing review for {review_id}"
                )
                await agent_instance.perform_review(review_id, args.channel)
                # The perform_review method will handle its own broadcasting and lifecycle
            else:
                logger.info(
                    f"{agent_instance.agent_id} starting coordination for task: {args.task}"
                )
                await agent_instance.coordinate(args.task)

        except KeyboardInterrupt:
            logger.info(f"{agent_instance.agent_id} interrupted.")
        finally:
            await agent_instance._disconnect_from_bus()

    asyncio.run(main())
