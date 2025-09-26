"""Single Constitutional AI Agent - Data-driven from registry."""

import logging
import asyncio
from typing import List, Optional
import uuid

try:
    import cogency
except ImportError:  # pragma: no cover - optional dependency for live runs
    cogency = None

from ..core.config import Config
from ..core.event import Event
from ..core.khala import Khala
from .registry import get_agent_data
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
        self.agent_id = f"{agent_type}-{uuid.uuid4().hex[:6]}"
        self.identity_index = 0
        self._load_identity()

        # Initialize cogency for LLM agents with constitutional identity
        self.cogency_agent = (
            cogency.Agent(
                llm="gemini",
                instructions=self._build_instructions(),
                tools=self.tools(),
            )
            if cogency
            else None
        )

    def _load_identity(self):
        """Load agent configuration from registry."""
        self.registry_data = get_agent_data(self.agent_type)
        if not self.registry_data:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

    def tools(self) -> List[str]:
        """Get the tools available to this agent."""
        return self.registry_data["tools"]

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
        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed to send message: {e}")
            raise

    async def _process_message(self, event: Event):
        """Process an incoming message from the Bus."""
        if event.type == "agent_message":
            if self.cogency_agent:
                async for cogency_event in self.cogency_agent(event.content):
                    if cogency_event["type"] == "respond":
                        response_content = cogency_event["content"]
                        await self.send_message(content=response_content)
                        if "!despawn" in response_content.lower():
                            self._running = False
                            break  # Exit streaming loop if despawn signal received
                    # Handle other cogency_event types if necessary
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

                async for cogency_event in self.cogency_agent(
                    f"Channel history:\n{history_text}"
                ):
                    logger.info(
                        f"Agent {self.agent_id} cogency event: {cogency_event['type']}"
                    )
                    if cogency_event["type"] == "respond":
                        # Agent orientation response - send to channel
                        logger.info(
                            f"Agent {self.agent_id} sending cogency response: {cogency_event['content'][:100]}..."
                        )
                        await self.send_message(content=cogency_event["content"])
                        break
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
            async for event in self.khala.listen():
                await self._process_message(event)
        except asyncio.CancelledError:
            pass  # Agent was cancelled, graceful shutdown
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
