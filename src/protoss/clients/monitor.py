"""The Lens of Providence: A real-time monitor for the Protoss swarm using Textual."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import time

import websockets
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Footer, Log, Tree
from textual.reactive import reactive

from ..core.config import Config


class MonitorApp(App):
    """A Textual app to monitor the Protoss swarm in real-time."""

    CSS_PATH = "monitor.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    channels = reactive(dict)
    agents = reactive(dict)

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._log_widget = None
        self._channel_tree = None
        self._agent_tree = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        self._log_widget = Log(highlight=True, id="log_stream")
        self._channel_tree = Tree("Channels", id="channels")
        self._agent_tree = Tree("Agents", id="agents")

        yield Header()
        yield Container(
            VerticalScroll(self._channel_tree, self._agent_tree, id="sidebar"),
            self._log_widget,
            id="app-grid",
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.title = "Lens of Providence"
        self.sub_title = f"Monitoring the Khala at {self.config.bus_url}"
        asyncio.create_task(self.run_client())

    def _format_message(self, event: Dict[str, Any]) -> str:
        """Formats a structured event into a rich-text string for the Log widget."""
        now = datetime.fromtimestamp(event.get("timestamp", time.time())).strftime(
            "%H:%M:%S"
        )
        event_type = event.get("type", "unknown_event")
        channel = event.get("channel", "unknown")
        sender = event.get("sender", "system")
        coordination_id = event.get("coordination_id", "N/A")

        # Default content for non-agent_message events
        content_display = f"[yellow]{event_type}[/]"

        if event_type == "agent_message":
            message_content = event.get("content", "")
            content_display = message_content
        elif event_type == "coordination_complete":
            result = event.get("payload", {}).get("result", "Coordination finished.")
            content_display = f"[green]COORDINATION COMPLETE:[/][white] {result}[/]"
        elif event_type == "agent_spawn":
            agent_id = event.get("payload", {}).get("agent_id", "unknown")
            agent_type = event.get("payload", {}).get("agent_type", "unknown")
            content_display = (
                f"[blue]Agent Spawned:[/][white] {agent_id} ({agent_type})[/]"
            )
        elif event_type == "agent_despawn":
            agent_id = event.get("payload", {}).get("agent_id", "unknown")
            agent_type = event.get("payload", {}).get("agent_type", "unknown")
            content_display = (
                f"[red]Agent Despawned:[/][white] {agent_id} ({agent_type})[/]"
            )
        elif event_type == "agent_connected":
            agent_id = event.get("payload", {}).get("agent_id", "unknown")
            content_display = f"[green]Agent Connected:[/][white] {agent_id}[/]"
        elif event_type == "agent_disconnected":
            agent_id = event.get("payload", {}).get("agent_id", "unknown")
            content_display = f"[red]Agent Disconnected:[/][white] {agent_id}[/]"
        elif event_type == "vision_seed":
            vision = event.get("payload", {}).get("vision", "No vision provided")
            content_display = f"[magenta]Vision Seeded:[/][white] {vision}[/]"

        return f"[dim]{now}[/] | [blue]#{channel:<10}[/] | [cyan]{sender:<10}[/] | [purple]{coordination_id[:8]}[/] | {content_display}"

    def _update_trees(self, event: Dict[str, Any]):
        """Update the channel and agent trees with new data based on event types."""
        event_type = event.get("type")
        channel_name = event.get("channel")
        sender_id = event.get("sender")  # This is the agent_id for agent events

        if not channel_name or not sender_id:
            return

        # Ensure channel node exists
        if channel_name not in self.channels:
            channel_node = self._channel_tree.root.add(channel_name)
            self.channels[channel_name] = channel_node
        else:
            channel_node = self.channels[channel_name]

        if event_type == "agent_spawn":
            agent_id = event.get("payload", {}).get("agent_id", sender_id)
            if agent_id not in self.agents:
                agent_node = channel_node.add_leaf(agent_id)
                self.agents[agent_id] = agent_node
                agent_node.set_attribute("status", "online")
                agent_node.update_render()
        elif event_type == "agent_despawn":
            agent_id = event.get("payload", {}).get("agent_id", sender_id)
            if agent_id in self.agents:
                agent_node = self.agents[agent_id]
                agent_node.set_attribute("status", "offline")
                agent_node.update_render()
                # Optionally remove or grey out despawned agents

    async def run_client(self):
        """The main loop to connect, listen, and update the UI."""
        uri = f"{self.config.bus_url}/monitor"
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    self.sub_title = f"Monitoring the Khala at {self.config.bus_url} [green]CONNECTED[/]"
                    await websocket.send(json.dumps({"type": "monitor_req"}))
                    ack = await websocket.recv()
                    if json.loads(ack).get("type") != "monitor_ack":
                        self._log_widget.write_line(
                            "[red]Failed to register as monitor.[/]"
                        )
                        return

                    async for raw_message in websocket:
                        msg = json.loads(raw_message)
                        formatted_msg = self._format_message(msg)
                        self._log_widget.write_line(formatted_msg)
                        self._update_trees(msg)

            except (
                websockets.exceptions.ConnectionClosed,
                ConnectionRefusedError,
            ) as e:
                self.sub_title = f"Monitoring the Khala at {self.config.bus_url} [red]DISCONNECTED[/]"
                self._log_widget.write_line(
                    f"[red]Lens disconnected: {e}. Retrying...[/]"
                )
                await asyncio.sleep(5)
            except Exception as e:
                self._log_widget.write_line(
                    f"[bold red]An unexpected error occurred: {e}[/]"
                )
                break
