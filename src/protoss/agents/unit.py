import asyncio
import json
import logging
import uuid
import websockets
import argparse
from typing import List, Optional, Tuple
from ..constitution import SWARM_CONSTITUTION, COORDINATION_PATTERNS
from ..core.config import Config

logger = logging.getLogger(__name__)


class Unit:
    """Pure constitutional AI coordination agent interface."""

    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        channel_id: str,
        config: Config,
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.channel_id = channel_id
        self.config = config
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._listen_task: Optional[asyncio.Task] = None

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
            await self._websocket.send(json.dumps({"type": "join_channel", "channel": self.channel_id}))
        except Exception as e:
            logger.error(f"{self.agent_id} failed to connect to Bus: {e}")
            self._websocket = None

    async def _disconnect_from_bus(self):
        """Close WebSocket connection to the Bus."""
        if self._websocket and (self._websocket.state == websockets.protocol.State.OPEN):
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
            
            async for event in agent("Apply your constitutional perspective to this context."):
                if event["type"] == "respond":
                    response_text += event.get("content", "")
                    
            return response_text
            
        except ImportError:
            return f"Constitutional reasoning unavailable: {self.__class__.__name__} perspective needed but Cogency not available."

    async def broadcast(self, response: str):
        """Pure broadcast layer - response only."""
        if not self._websocket or not (self._websocket.state == websockets.protocol.State.OPEN):
            logger.warning(f"{self.agent_id} websocket not open, cannot broadcast message.")
            return

        message = {"type": "msg", "channel": self.channel_id, "content": response, "sender": self.agent_id}
        try:
            await self._websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"{self.agent_id} failed to broadcast message: {e}")

    async def coordinate(self, context: str):
        """Pure constitutional coordination."""
        from cogency.core.agent import Agent
        
        instructions = f"""\
{SWARM_CONSTITUTION}

{self.identity}

{COORDINATION_PATTERNS}
"""
        
        agent = Agent(instructions=instructions, tools=self.tools)
        
        response_text = ""
        async for event in agent(context):
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
    parser.add_argument("--agent-type", required=True, help="Type of the agent (e.g., zealot, archon).")
    parser.add_argument("--channel", required=True, help="Channel ID for coordination.")
    parser.add_argument("--config-json", required=True, help="JSON string of the agent's configuration.")
    parser.add_argument("--task", required=True, help="The task context for the agent.")
    
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    async def main():
        config_data = json.loads(args.config_json)
        config = Config.from_dict(config_data)

        # Dynamically create agent instance based on agent_type
        # This assumes agent classes are imported or can be dynamically loaded
        # For now, we'll use a simple mapping for demonstration
        if args.agent_type == "zealot":
            from .zealot import Zealot
            agent_instance = Zealot(args.agent_id, args.agent_type, args.channel, config)
        elif args.agent_type == "archon":
            from .archon import Archon
            agent_instance = Archon(args.agent_id, args.agent_type, args.channel, config)
        elif args.agent_type == "arbiter":
            from .arbiter import Arbiter
            agent_instance = Arbiter(args.agent_id, args.agent_type, args.channel, config)
        elif args.agent_type == "conclave":
            from .conclave import Conclave
            agent_instance = Conclave(args.agent_id, args.agent_type, args.channel, config)
        else:
            logger.error(f"Unknown agent type: {args.agent_type}")
            return

        await agent_instance._connect_to_bus()
        try:
            logger.info(f"{agent_instance.agent_id} starting coordination for task: {args.task}")
            await agent_instance.coordinate(args.task)

        except KeyboardInterrupt:
            logger.info(f"{agent_instance.agent_id} interrupted.")
        finally:
            await agent_instance._disconnect_from_bus()

    asyncio.run(main())
