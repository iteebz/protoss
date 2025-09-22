"""Agent gateway for spawning and lifecycle management."""

import asyncio
import json
import logging
import websockets
import subprocess
from typing import Dict, Any, Callable, Optional, List
from dataclasses import asdict

from ..core.config import Config
from ..core.lifecycle import Lifecycle
from ..core.message import Message
from ..core.protocols import Signal
from ..core import parser
from ..core.bus import BusClient
from ..agents.probe import Probe

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

    async def _send_to_bus(
        self,
        channel: str,
        event: Optional[Dict] = None,
        signals: Optional[List[Signal]] = None,
    ):
        """Send a system message to a channel on the Bus using the existing websocket."""
        if not self.websocket or not (
            self.websocket.state == websockets.protocol.State.OPEN
        ):
            logger.warning("Gateway websocket not open, cannot send message to Bus.")
            return

        message_to_send = Message(
            channel=channel,
            sender="gateway",
            event=event,
            signals=signals if signals is not None else [],
        )
        try:
            # Serialize Message dataclass to dict for JSON transmission
            await self.websocket.send(json.dumps(asdict(message_to_send)))
        except Exception as e:
            logger.error(f"Gateway failed to send message to Bus: {e}")

    async def _spawn_process(
        self,
        agent_type: str,
        channel_id: str,
        agent_params: Optional[Dict] = None,
    ):
        """Create a new agent process and announce it."""
        agent_id = self.lifecycle.spawn(agent_type, channel_id)

        if not agent_id:
            logger.warning(
                f"Could not spawn {agent_type} in {channel_id}: capacity full or unknown type."
            )
            # Create an event dictionary for the message
            event = {
                "type": "system",
                "content": f"⚠️ Cannot spawn '{agent_type}': Maximum agents reached or unknown type.",
            }
            await self._send_to_bus(channel_id, event=event)
            return

        logger.info(f"Gateway is spawning {agent_id} in {channel_id}...")

        # Command to run the agent unit as a separate process, without the `--task` parameter.
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
        ]

        if agent_params:
            cmd.extend(["--params", json.dumps(agent_params)])

        try:
            # Launch the subprocess
            await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            event = {"type": "system", "content": f"✨ {agent_id} has been warped in."}
            await self._send_to_bus(channel_id, event=event)

        except Exception as e:
            logger.error(f"Failed to launch subprocess for {agent_id}: {e}")
            event = {"type": "system", "content": f"❌ Failed to warp in {agent_id}."}
            await self._send_to_bus(channel_id, event=event)
            self.lifecycle.despawn(agent_id)

    async def _spawn_probe(self, channel_id: str, summoning_message: str):
        """Spawns a Probe heuristic agent."""
        logger.info(f"Gateway is spawning a Probe in {channel_id}...")

        bus_client = BusClient(self.config.bus_url)
        await bus_client.connect()

        try:
            probe = Probe(bus_connection=bus_client)
            probe.execute(summoning_message)
            event = {
                "type": "system",
                "content": "✨ Probe has been warped in and completed its task.",
            }
            await self._send_to_bus(channel_id, event=event)
        except Exception as e:
            logger.error(f"Failed to execute Probe: {e}")
            event = {"type": "system", "content": "❌ Failed to execute Probe."}
            await self._send_to_bus(channel_id, event=event)
        finally:
            await bus_client.disconnect()

    async def _handle_message(self, raw_message: str):
        """Parse and dispatch incoming messages from the bus."""
        try:
            message_dict = json.loads(raw_message)
            # Reconstruct the Message object to work with our protocol.
            message = Message(
                sender=message_dict.get("sender"),
                channel=message_dict.get("channel"),
                timestamp=message_dict.get("timestamp"),
                event=message_dict.get("event", {}),
                signals=[],  # Signals will be parsed fresh.
            )

            if message.sender == "gateway":
                return  # Do not process our own announcements.

            content = message.event.get("content", "")
            if not content:
                return  # No content to parse for signals.

            # Use the purified parser to find signals in the message content.
            signals = parser.signals(content)
            if not signals:
                return  # No signals for the Gateway to act on.

            channel_id = message.channel
            sender_id = message.sender

            # --- Sacred Guardrail Protocol (!despawn) ---
            if any(isinstance(s, Signal.Despawn) for s in signals):
                logger.info(
                    f"Gateway detected !despawn from {sender_id} in {channel_id}. Despawning agent."
                )
                self.lifecycle.despawn(sender_id)

            # --- Emergent Tasking Protocol (@mention) ---
            mention_signals = [s for s in signals if isinstance(s, Signal.Mention)]
            for s in mention_signals:
                agent_type = s.agent_name
                if agent_type == "probe":
                    logger.info(
                        f"Gateway detected @probe in {channel_id}. Spawning Probe heuristic agent."
                    )
                    # The Probe is a special case. It's a heuristic agent, not an LLM agent.
                    # We spawn it directly and pass the message content to its execute method.
                    asyncio.create_task(
                        self._spawn_probe(
                            channel_id=channel_id,
                            summoning_message=content,
                        )
                    )
                # Check if an agent of this type is already active in the channel.
                elif not self.lifecycle.get_active_agent_id(agent_type, channel_id):
                    logger.info(
                        f"Gateway detected @{agent_type} in {channel_id}. No active agent found, spawning new agent."
                    )
                    # Spawn the agent without a task, as per the scripture.
                    # The new agent will orient itself from the channel history.
                    asyncio.create_task(
                        self._spawn_process(
                            agent_type=agent_type,
                            channel_id=channel_id,
                        )
                    )

        except json.JSONDecodeError:
            logger.warning(f"Gateway received invalid JSON: {raw_message}")
        except Exception as e:
            logger.error(f"Error in Gateway message handler: {e}")
