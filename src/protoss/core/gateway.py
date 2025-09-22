"""Agent gateway for spawning and lifecycle management."""

import asyncio
import json
import logging
import websockets
import subprocess
from typing import Dict, Any, Callable, Optional
from .config import Config
from .lifecycle import Lifecycle
from . import parser
from .protocols import Signals

logger = logging.getLogger(__name__)


class Gateway:
    """Manages agent spawning by listening to the Bus as a network client."""

    def __init__(
        self,
        config: Config,
        max_agents_per_channel: int = 10,
        factories: Dict[str, Callable[[str], Any]] = None,
    ):
        self.config = config
        self.websocket: websockets.WebSocketClientProtocol = None
        self.lifecycle = Lifecycle(
            max_agents_per_channel=max_agents_per_channel,
            factories=factories or self._default_factories(),
        )
        self.channel_tasks: Dict[str, str] = {}
        self._listen_task = None

    def _default_factories(self) -> Dict[str, Callable[[str], Any]]:
        """Default agent factories for dependency injection."""
        from ..agents import Zealot, Archon, Arbiter, Conclave, Oracle

        return {
            "zealot": Zealot,
            "archon": Archon,
            "arbiter": Arbiter,
            "conclave": Conclave,
            "oracle": Oracle,
        }

    async def _send_to_bus(self, channel: str, content: str):
        """Send a system message to a channel on the Bus using the existing websocket."""
        if not self.websocket or not (
            self.websocket.state == websockets.protocol.State.OPEN
        ):
            logger.warning("Gateway websocket not open, cannot send message to Bus.")
            return

        message = {
            "type": "msg",
            "channel": channel,
            "sender": "gateway",
            "content": content,
        }
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Gateway failed to send message to Bus: {e}")

    async def _spawn_process(
        self,
        agent_type: str,
        channel_id: str,
        task: str,
        agent_params: Optional[Dict] = None,
    ):
        """Create a new agent process and announce it."""
        agent_id = self.lifecycle.spawn(agent_type, channel_id)

        if not agent_id:
            logger.warning(
                f"Could not spawn {agent_type} in {channel_id}: capacity full or unknown type."
            )
            await self._send_to_bus(
                channel_id,
                f"⚠️ Cannot spawn '{agent_type}': Maximum agents reached or unknown type.",
            )
            return

        logger.info(f"Gateway is spawning {agent_id} in {channel_id}...")

        # Command to run the agent unit as a separate process
        cmd = [
            "python",
            "-m",
            "protoss.agents.unit",
            "--agent-id",
            agent_id,
            "--agent-type",
            agent_type,
            "--channel",
            channel_id,
            "--bus-url",
            self.config.bus_url,
            "--task",
            task,
        ]

        if agent_params:
            cmd.extend(["--params", json.dumps(agent_params)])

        try:
            # Launch the subprocess
            await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            await self._send_to_bus(channel_id, f"✨ {agent_id} has been warped in.")

        except Exception as e:
            logger.error(f"Failed to launch subprocess for {agent_id}: {e}")
            await self._send_to_bus(channel_id, f"❌ Failed to warp in {agent_id}.")
            self.lifecycle.despawn(agent_id)

    async def _handle_message(self, raw_message: str):
        """Parse and dispatch incoming messages from the bus."""
        try:
            msg = json.loads(raw_message)
            msg_type = msg.get("type")
            channel_id = msg.get("channel")
            content = msg.get("content")
            sender = msg.get("sender")

            if msg_type != "msg" or sender == "gateway":
                return

            if channel_id == "gateway_commands":
                vision_data = json.loads(content)
                if vision_data.get("type") == "vision":
                    vision_channel = vision_data.get("channel")
                    vision_content = vision_data.get("content")
                    vision_params = vision_data.get("params", {})
                    logger.info(f"Gateway received vision: {vision_content}")

                    asyncio.create_task(
                        self._spawn_process(
                            agent_type="archon",
                            channel_id=vision_channel,
                            task=f"seed channel for: {vision_content}",
                            agent_params={"action": "seed_channel"},
                        )
                    )

                    agent_type = vision_params.get("initial_agent", "zealot")
                    agent_count = vision_params.get("agent_count", 1)

                    for _ in range(agent_count):
                        asyncio.create_task(
                            self._spawn_process(
                                agent_type=agent_type,
                                channel_id=vision_channel,
                                task=vision_content,
                            )
                        )
                return

            signals = parser.parse_signals(content)

            mention_signals = [
                s for s in signals if isinstance(s, Signal.Mention)
            ]
            spawn_signals = [s for s in signals if isinstance(s, Signal.Spawn)]

            # Handle direct @mention spawning
            for s in mention_signals:
                agent_type = s.agent_name
                logger.info(
                    f"Detected @mention {agent_type} in {channel_id}. Spawning agent to respond."
                )
                asyncio.create_task(
                    self._spawn_process(
                        agent_type=agent_type,
                        channel_id=channel_id,
                        task=content,  # The original message content is the task
                        agent_params={"action": "respond_to_mention"},
                    )
                )

            # Handle @spawn requests
            task = self.channel_tasks.get(channel_id, "")  # Define task here
            if not task:
                logger.warning(
                    f"No task found for channel {channel_id} to spawn agent."
                )

            for s in spawn_signals:
                agent_type = s.agent_type
                logger.info(f"Detected @spawn {agent_type} in {channel_id}.")
                asyncio.create_task(self._spawn_process(agent_type, channel_id, task))

            # Handle !archive signal
            archive_signals = [
                s for s in signals if isinstance(s, Signal.Archive)
            ]
            for s in archive_signals:
                summary = s.summary
                logger.info(
                    f"Detected !archive in {channel_id}. Archiving work for review."
                )
                asyncio.create_task(
                    self._spawn_process(
                        agent_type="archon",
                        channel_id=channel_id,
                        task=summary,  # The summary is the task for the Archon
                        agent_params={"action": "archive_for_review"},
                    )
                )

            # Handle !review <review_id> signal
            review_signals = [s for s in signals if isinstance(s, Signal.Review)]
            for s in review_signals:
                review_id = s.review_id
                logger.info(
                    f"Detected !review {review_id} in {channel_id}. Chalice offered."
                )

            # Handle !reviewing <review_id> signal
            reviewing_signals = [
                s for s in signals if isinstance(s, Signal.Reviewing)
            ]
            for s in reviewing_signals:
                review_id = s.review_id
                logger.info(
                    f"Detected !reviewing {review_id} in {channel_id}. Chalice accepted."
                )

            # Handle !reviewed <review_id> [judgment] signal
            reviewed_signals = [
                s for s in signals if isinstance(s, Signal.Reviewed)
            ]
            for s in reviewed_signals:
                review_id = s.review_id
                judgment = s.judgment
                logger.info(
                    f"Detected !reviewed {review_id} with judgment '{judgment}' in {channel_id}. Chalice returned."
                )

        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"Error in Gateway message handler: {e}")
