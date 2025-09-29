"""Single Constitutional AI Agent - Data-driven from registry."""

import logging
import asyncio
from typing import List, Optional
import uuid

try:
    import cogency
except ImportError:  # pragma: no cover - optional dependency for live runs
    cogency = None

from .config import Config
from .event import Event
from .khala import Khala
from ..constitution.registry import get_agent_data
from ..constitution import assemble


logger = logging.getLogger(__name__)


class Agent:
    """Pure constitutional AI coordination agent - data-driven from registry."""

    def __init__(
        self,
        agent_type: str,
        channel: str,
        bus_url: str,
        coordination_id: str,
        config: Optional[Config] = None,
    ):
        self.agent_type = agent_type
        self.channel = channel
        self.coordination_id = coordination_id
        runtime_bus_url = bus_url or (config.bus_url if config else None)
        if config is None:
            self.config = Config(bus_url=runtime_bus_url or Config().bus_url)
        else:
            self.config = config
        self.bus_url = runtime_bus_url or self.config.bus_url
        self.khala: Khala = Khala(bus_url=self.bus_url)  # Instantiate Khala here
        self._running = True
        self._shutdown_event = asyncio.Event()
        self.agent_id = f"{agent_type}-{uuid.uuid4().hex[:6]}"
        self.identity_index = 0
        self._load_identity()

        # Initialize cogency for LLM agents with constitutional identity
        logger.debug(
            f"Initializing cogency agent, cogency available: {cogency is not None}"
        )
        self.cogency_agent = (
            cogency.Agent(
                llm="gemini",
                instructions=self._build_instructions(),
                tools=self.tools(),
            )
            if cogency
            else None
        )
        logger.debug(f"Cogency agent created: {self.cogency_agent is not None}")

    def _load_identity(self):
        """Load agent configuration from registry."""
        self.registry_data = get_agent_data(self.agent_type)
        if not self.registry_data:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

    def tools(self) -> List:
        """Get the tools available to this agent."""
        tool_categories = self.registry_data["tools"]
        tools = []
        
        for category in tool_categories:
            if category == "infra":
                from ..tools.infra.channel import ChannelCreate
                from ..tools.infra.agent import AgentSpawn
                tools.extend([ChannelCreate(), AgentSpawn()])
        
        return tools

    def _build_instructions(self) -> str:
        """Build constitutional instructions for cogency agent."""
        return assemble(
            self.agent_type, self.agent_id, self.channel, self.identity_index
        )

    async def broadcast(self, event: dict):
        """Broadcast an event to the channel."""
        await self.send_message(
            content=event["content"],
            event_type=event["type"],
            event_payload=event,
            coordination_id=self.coordination_id,
        )

    async def send_message(
        self,
        content: str,
        event_type: str = "agent_message",
        event_payload: Optional[dict] = None,
        coordination_id: Optional[str] = None,
    ):
        """Send a message to the Bus."""
        message = {
            "channel": self.channel,
            "sender": self.agent_id,
            "type": event_type,
            "content": content,
            "coordination_id": coordination_id or self.coordination_id,
            "payload": event_payload if event_payload is not None else {},
        }
        logger.info(f"Agent {self.agent_id} sending message: {message}")

        try:
            await self.khala.send(message)
            logger.info(f"Agent {self.agent_id} message sent successfully")
        except ConnectionError:
            logger.info(f"Khala severed, agent {self.agent_id} departing gracefully")
            import sys

            sys.exit(0)
        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed to send message: {e}")
            raise

    async def join_coordination(self, coordination_id: str, target_channel: str):
        """Join a coordination by fetching cross-channel context and switching to target channel."""
        logger.info(
            f"Arbiter {self.agent_id} joining coordination {coordination_id} in {target_channel}"
        )

        try:
            # Fetch full coordination history across all channels
            coordination_history = await self.khala.request_history(
                coordination_id=coordination_id
            )
            logger.info(
                f"Arbiter {self.agent_id} loaded {len(coordination_history)} coordination messages"
            )

            # Switch to target channel
            self.channel = target_channel
            self.coordination_id = coordination_id

            # Process coordination context through cogency
            if self.cogency_agent and coordination_history:
                history_text = "\n".join(
                    [
                        f"[{msg.get('channel', 'unknown')}] {msg.get('sender', 'unknown')}: {msg.get('content', '')}"
                        for msg in coordination_history
                    ]
                )

                async for cogency_event in self.cogency_agent(
                    f"Coordination context (ID: {coordination_id}):\n{history_text}"
                ):
                    if cogency_event["type"] == "respond":
                        # Arbiter synthesizes coordination context and reports
                        await self.send_message(content=cogency_event["content"])
                        break

            return True

        except Exception as e:
            logger.error(
                f"Arbiter {self.agent_id} failed to join coordination {coordination_id}: {e}"
            )
            return False

    async def shutdown(self):
        """Signal agent to shutdown gracefully."""
        logger.info(f"Agent {self.agent_id} shutdown signal received")
        self._running = False
        self._shutdown_event.set()

    async def _listen_for_events(self):
        """Listen for events until shutdown."""
        async for event in self.khala.listen():
            await self._process_message(event)
            if not self._running:
                break

    async def _process_with_cogency(self, content: str):
        """Process content through cogency LLM and handle responses."""
        async for cogency_event in self.cogency_agent(content):
            if cogency_event["type"] == "respond":  # §respond event from doctrine
                response_content = cogency_event["content"]
                await self.send_message(content=response_content)
                if "!despawn" in response_content.lower():
                    logger.info(f"Agent {self.agent_id} received despawn signal")
                    self._running = False
                    break

    async def _process_message(self, event: Event):
        """Process an incoming message from the Bus."""
        # Handle system shutdown signal
        if event.type == "system_shutdown":
            logger.info(f"Agent {self.agent_id} received system shutdown")
            await self.shutdown()
            return

        if event.type == "agent_message":
            if self.cogency_agent:
                await self._process_with_cogency(event.content)
            else:
                logger.warning(f"Cogency agent not initialized for {self.agent_type}")
                self._running = False  # Despawn if no cogency to process message

    async def run(self):
        """Agent main loop."""
        logger.info(
            f"Agent {self.agent_id} ({self.agent_type}) online in {self.channel}"
        )
        await self.khala.connect(agent_id=self.agent_id)

        # Context assembly - request channel history before entering coordinate loop
        try:
            history = await self.khala.request_history(self.channel)
            logger.info(
                f"Agent {self.agent_id} loaded {len(history)} historical messages"
            )

            # Process channel history through cogency agent for constitutional context
            logger.info(
                f"Agent {self.agent_id} cogency_agent: {self.cogency_agent is not None}, history length: {len(history)}"
            )

            if self.cogency_agent and history:
                history_text = "\n".join(
                    [
                        f"{msg.get('sender', 'unknown')}: {msg.get('content', '')}"
                        for msg in history
                    ]
                )
                logger.info(
                    f"Agent {self.agent_id} processing history through cogency: {history_text[:200]}..."
                )
                await self._process_with_cogency(f"Channel history:\n{history_text}")
            else:
                logger.warning(
                    f"Agent {self.agent_id} skipping cogency processing - cogency_agent: {self.cogency_agent is not None}, history: {len(history)}"
                )

        except Exception as e:
            logger.warning(f"Failed to load channel history: {e}")
            history = []

        await self.send_message(
            content=f"Agent {self.agent_id} ({self.agent_type}) spawned.",
            event_type="system_message",
            event_payload={
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "channel": self.channel,
                "coordination_id": self.coordination_id,
            },
        )

        try:
            # Run until shutdown signal or cancellation
            listen_task = asyncio.create_task(self._listen_for_events())
            shutdown_task = asyncio.create_task(self._shutdown_event.wait())

            done, pending = await asyncio.wait(
                [listen_task, shutdown_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        except asyncio.CancelledError:
            logger.info(f"Agent {self.agent_id} cancelled - shutting down gracefully")
        except Exception as e:
            logger.error(f"Agent {self.agent_id} error: {e}")
            raise
        finally:
            logger.info(f"Agent {self.agent_id} ({self.agent_type}) offline.")
            await self.send_message(
                content=f"Agent {self.agent_id} ({self.agent_type}) despawned.",
                event_type="system_message",
                event_payload={
                    "agent_id": self.agent_id,
                    "agent_type": self.agent_type,
                    "channel": self.channel,
                    "coordination_id": self.coordination_id,
                },
            )


def main():
    """CLI entry point for running an Agent."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run a Protoss Agent.")
    parser.add_argument("--agent-type", required=True, help="Type of the agent")
    parser.add_argument("--channel", required=True, help="Channel to connect to")
    parser.add_argument("--bus-url", required=True, help="URL of the Bus")
    parser.add_argument("--agent-id", help="Optional: ID of the agent")
    parser.add_argument("--coordination-id", help="Optional: Coordination ID")
    parser.add_argument(
        "--params",
        type=json.loads,
        default={},
        help="Optional: JSON string of additional parameters",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    agent = Agent(
        agent_type=args.agent_type,
        channel=args.channel,
        bus_url=args.bus_url,
        coordination_id=args.coordination_id or uuid.uuid4().hex,
    )

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(agent.run())
    except KeyboardInterrupt:
        logger.info(f"Agent {agent.agent_id} shutting down.")
    except Exception as e:
        logger.error(f"Agent {agent.agent_id} encountered an error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
