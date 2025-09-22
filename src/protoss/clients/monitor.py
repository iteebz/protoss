"""The Lens of Providence: A real-time monitor for the Protoss swarm using Textual."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

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

    def _format_message(self, msg: Dict[str, Any]) -> str:
        """Formats a message from the bus into a rich-text string for the Log widget."""
        now = datetime.now().strftime("%H:%M:%S")
        channel = msg.get("channel", "unknown")
        sender = msg.get("sender", "system")
        content = msg.get("content", "")

        # Use Textual's rich markup
        return f"[dim]{now}[/] | [blue]#{channel:<15}[/] | [cyan]{sender:<15}[/] | {content}"

        def _update_trees(self, msg: Dict[str, Any]):
            """Update the channel and agent trees with new data."""
            channel_name = msg.get("channel")
            sender_id = msg.get("sender")

            if not channel_name or not sender_id or sender_id in ["system", "gateway"]:
                return

            # Ensure channel node exists
            if channel_name not in self.channels:
                channel_node = self._channel_tree.root.add(channel_name)
                self.channels[channel_name] = channel_node
            else:
                channel_node = self.channels[channel_name]

            # Add agent to channel node if not already present
            if sender_id not in self.agents:
                agent_node = channel_node.add_leaf(sender_id)
                self.agents[sender_id] = agent_node

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
