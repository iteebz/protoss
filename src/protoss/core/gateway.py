"""Agent gateway for spawning and lifecycle management."""

import asyncio
import json
import logging
import re
import websockets
import subprocess
from typing import Dict, Any, Callable
import argparse # Added for main() function
import json # Added for main() function

from .lifecycle import Lifecycle
from . import mentions

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

    def _default_factories(self) -> Dict[str, Callable[[str], Any]]:
        """Default agent factories for dependency injection."""
        from ..agents import Zealot, Archon, Arbiter, Conclave

        return {
            "zealot": Zealot,
            "archon": Archon,
            "arbiter": Arbiter,
            "conclave": Conclave,
        }

    async def _send_to_bus(self, channel: str, content: str):
        """Send a system message to a channel on the Bus."""
        message = {
            "type": "msg",
            "channel": channel,
            "sender": "gateway",
            "content": content,
        }
        try:
            # Use a short-lived connection for sending messages
            async with websockets.connect(f"{self.config.bus_url}/gateway") as ws:
                await ws.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Gateway failed to send message to Bus: {e}")

    async def _spawn_process(self, agent_type: str, channel_id: str, task: str):
        """Create a new agent process and announce it."""
        agent_id = self.lifecycle.spawn(agent_type, channel_id)

        if not agent_id:
            logger.warning(f"Could not spawn {agent_type} in {channel_id}: capacity full or unknown type.")
            await self._send_to_bus(
                channel_id,
                f"⚠️ Cannot spawn '{agent_type}': Maximum agents reached or unknown type."
            )
            return

        logger.info(f"Gateway is spawning {agent_id} in {channel_id}...")
        
        # Prepare config for the agent subprocess
        agent_config_data = self.config.to_dict()
        # Override bus_url for the agent if necessary, though it should be in config
        agent_config_data["bus_url"] = self.config.bus_url
        # Pass the task explicitly as it's dynamic
        agent_config_data["task"] = task

        # Command to run the agent unit as a separate process
        cmd = [
            "python", "-m", "protoss.agents.unit",
            "--agent-id", agent_id,
            "--agent-type", agent_type,
            "--channel", channel_id,
            "--config-json", json.dumps(agent_config_data),
        ]

        try:
            # Launch the subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            await self._send_to_bus(channel_id, f"✨ {agent_id} has been warped in.")
            
            # Optionally, you can manage the process lifecycle further,
            # e.g., by storing the process object in AgentState and monitoring it.
            # For now, we launch and forget.

        except Exception as e:
            logger.error(f"Failed to launch subprocess for {agent_id}: {e}")
            await self._send_to_bus(channel_id, f"❌ Failed to warp in {agent_id}.")
            # Clean up the state if the process fails to start
            self.lifecycle.despawn(agent_id)

    async def _handle_message(self, raw_message: str):
        """Parse and dispatch incoming messages from the bus."""
        try:
            msg = json.loads(raw_message)
            if msg.get("type") != "msg":
                return # The gateway only cares about standard messages

            content = msg.get("content", "")
            channel = msg.get("channel")
            sender = msg.get("sender")

            # Handle !spawn command
            spawn_match = re.search(r"!spawn\s+(\w+)\s*(.*)", content)
            if spawn_match:
                agent_type = spawn_match.group(1)
                task = spawn_match.group(2) or "Assigned to coordinate."
                asyncio.create_task(self._spawn_process(agent_type, channel, task))
                return

            # Handle !despawn command
            despawn_match = re.search(r"!despawn\s+@?([\w-]+)", content)
            if despawn_match:
                agent_id = despawn_match.group(1)
                if self.lifecycle.despawn(agent_id):
                    asyncio.create_task(self._send_to_bus(channel, f"💀 {agent_id} has been recalled."))
                else:
                    asyncio.create_task(self._send_to_bus(channel, f"❓ Cannot recall '{agent_id}': Not found."))
                return

            # Handle !rebirth command
            rebirth_match = re.search(r"!rebirth\s+@?([\w-]+)", content)
            if rebirth_match:
                target_id = rebirth_match.group(1)
                agent_state = self.lifecycle.agent_registry.get(target_id)

                if not agent_state:
                    asyncio.create_task(self._send_to_bus(channel, f"❓ Cannot rebirth '{target_id}': Not found."))
                    return
                
                if agent_state.channel_id != channel:
                    asyncio.create_task(self._send_to_bus(channel, f"❌ {target_id} is not in this channel."))
                    return

                if sender == target_id:
                    asyncio.create_task(self._send_to_bus(channel, f"🚫 Self-rebirth is not permitted."))
                    return

                # Announce the despawn and then spawn the successor
                if self.lifecycle.despawn(target_id):
                    await self._send_to_bus(channel, f"💀 {target_id} archived at request of {sender}. Beginning rebirth...")
                    agent_type = agent_state.agent_type
                    task = f"Successor to {target_id}."
                    asyncio.create_task(self._spawn_process(agent_type, channel, task))
                return

            # Handle @mentions
            mentions_list = mentions.extract_mentions(content)
            for mention in mentions_list:
                # Check if it's a specific agent ID
                if mention in self.lifecycle.agent_registry:
                    result = self.lifecycle.respawn(mention)
                    if result.get("status") == "success":
                        asyncio.create_task(self._send_to_bus(channel, f"🔄 {mention} has been reactivated."))
                    # Silently ignore if already active or not found, to avoid spam
                    continue

                # Check if it's a generic agent type
                if mention in self.lifecycle.factories:
                    task = f"Summoned by {sender}."
                    asyncio.create_task(self._spawn_process(mention, channel, task))
                    continue

        except json.JSONDecodeError:
            logger.warning(f"Gateway received invalid JSON: {raw_message}")

    async def listen(self):
        """Connect to the Bus and listen for messages indefinitely."""
        uri = f"{self.config.bus_url}/gateway"
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    self.websocket = websocket
                    logger.info(f"Gateway connected to Bus at {self.config.bus_url}")
                    async for raw_message in websocket:
                        await self._handle_message(raw_message)
            except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
                logger.error(f"Gateway connection to Bus failed: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"An unexpected error occurred in the Gateway: {e}")
                break # Exit on unexpected errors


async def main():
    """Entrypoint for running the Gateway daemon."""
    parser = argparse.ArgumentParser(description="Protoss Gateway Daemon")
    parser.add_argument("--config-json", required=True, help="JSON string of the Gateway's Config.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    from .config import Config
    config_data = json.loads(args.config_json)
    config = Config.from_dict(config_data)

    gateway = Gateway(config=config)
    await gateway.listen()

if __name__ == "__main__":
    asyncio.run(main())
