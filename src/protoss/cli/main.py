"""Protoss CLI interface."""

import asyncio
import logging
import typer

from typing import Optional
from uuid import uuid4
from protoss import Protoss
from ..core.config import Config
from ..core.khala import Khala
from .inspect import ProtossInspector

# Enable protoss logging
logging.basicConfig(level=logging.INFO)


app = typer.Typer(
    help="AI coordination through emergent agent swarms.", no_args_is_help=True
)


def coordinate(
    vision: str,
    port: int = 8888,
    coordination_id: Optional[str] = None,  # New: Allow specifying coordination_id
):
    """Core coordination interface."""

    async def run_coordination():
        try:
            current_coordination_id = (
                coordination_id if coordination_id else str(uuid4())
            )
            print(f"Initiating coordination: {current_coordination_id} - {vision}")
            async with Protoss(
                vision, port=port, coordination_id=current_coordination_id
            ) as swarm:
                result = await swarm
                print(f"Coordination complete: {result}")
        except Exception as e:
            print(f"Coordination failed: {e}")
            import traceback

            traceback.print_exc()

    asyncio.run(run_coordination())


# Remove callback - let typer handle commands normally


@app.command()
def coord(
    vision: str = typer.Argument(..., help="Vision to manifest"),
    port: int = typer.Option(8888, "--port", "-p", help="Bus port"),
    coordination_id: Optional[str] = typer.Option(
        None,
        "--coordination-id",
        "-id",
        help="Optional ID for the coordination session.",
    ),
):
    """Alternative coordination command."""
    coordinate(vision, port, coordination_id)


@app.command()
def nuke():
    """Nuclear option - clear all protoss and cogency data."""
    import shutil
    import os

    paths_to_nuke = [".protoss", ".cogency"]
    for path in paths_to_nuke:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"Nuked {path}")
        else:
            print(f"{path} not found")
    print("Nuclear purification complete.")


@app.command()
def status():
    """Show Protoss coordination system status."""

    async def show_status():
        config = Config()
        khala = Khala(bus_url=config.bus_url)
        try:
            await khala.connect(client_id="status_client")
            await khala.send(
                {
                    "type": "status_req",
                    "channel": "system",
                    "sender": "status_client",
                    "payload": {},
                }
            )

            response_message = await khala.receive()
            if response_message and response_message.msg_type == "status_resp":
                status_data = response_message.event

                print("Protoss Status")
                print(f"Status: {status_data.get('status', 'unknown')}")

                if status_data.get("status") == "online":
                    bus_snapshot = status_data.get("bus", {})
                    print(
                        "Bus metrics: "
                        f"channels={bus_snapshot.get('channels', 0)} "
                        f"agents={bus_snapshot.get('agents', 0)} "
                        f"messages={bus_snapshot.get('messages', 0)}"
                    )
            else:
                print("Failed to get status response from Bus.")

        except ConnectionError:
            print("Could not connect to Protoss Bus. Is it running?")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await khala.disconnect()

    asyncio.run(show_status())


@app.command()
def monitor(
    port: int = typer.Option(
        8888, "--port", "-p", help="Port of the Bus to connect to"
    ),
):
    """Live monitor for the swarm."""
    from ..clients.monitor import MonitorApp

    config = Config(port=port)
    app = MonitorApp(config=config)
    app.run()


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question for the swarm."),
    channel_id: str = typer.Option(
        None, "--channel", "-c", help="Channel ID for the conversation."
    ),
    port: int = typer.Option(8888, "--port", "-p", help="Bus port"),
):
    """Ask the swarm a question via the Arbiter."""

    async def run_ask():
        config = Config(port=port)
        khala = Khala(bus_url=config.bus_url)

        if not channel_id:
            ask_channel_id = f"query:{uuid4().hex[:8]}:active"
        else:
            ask_channel_id = channel_id

        print(f"Asking swarm in channel {ask_channel_id}...")

        # Generate a coordination_id for the ask command
        ask_coordination_id = str(uuid4())

        try:
            await khala.connect(agent_id="human_asker")
            # Send the initial question, which implicitly joins the channel
            await khala.send(
                {
                    "type": "human_ask",
                    "channel": ask_channel_id,
                    "sender": "human",
                    "coordination_id": ask_coordination_id,
                    "content": f"{question} @arbiter",
                    "payload": {"content": question},
                }
            )
            print(f"Human: {question}")

            print("Waiting for Arbiter's response...")
            async for message in khala.listen():  # Listen for structured events
                if (
                    message
                    and message.type == "agent_message"
                    and message.channel == ask_channel_id
                ):
                    sender = message.sender
                    content = message.content or ""

                    if sender and sender.startswith("arbiter-"):
                        print(f"\nARBITER: {content}")
                        break
                    elif (
                        sender == "system" and "has joined the coordination" in content
                    ):
                        continue
                    elif sender != "human":
                        print(f"[{sender}]: {content}")

        except ConnectionError as e:
            print(f"Could not connect to Protoss Bus: {e}. Is it running?")
        except KeyboardInterrupt:
            print("\nAsk command interrupted by user.")
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback

            traceback.print_exc()
        finally:
            await khala.disconnect()

    asyncio.run(run_ask())


@app.command()
def list():
    """List all coordination sessions."""
    inspector = ProtossInspector()
    try:
        coordinations = inspector.list_coordinations()
        if not coordinations:
            print("No coordination sessions found.")
            return

        print(
            f"{'ID':<32} {'Channel':<12} {'Messages':<8} {'Agents':<20} {'Complete':<8} {'Last Activity'}"
        )
        print("-" * 100)

        for coord in coordinations:
            agents_str = (
                ",".join(coord.active_agents)[:18] + "..."
                if len(",".join(coord.active_agents)) > 18
                else ",".join(coord.active_agents)
            )
            complete_str = "✓" if coord.complete else "✗"

            print(
                f"{coord.coordination_id:<32} {coord.channel:<12} {coord.message_count:<8} {agents_str:<20} {complete_str:<8} {coord.last_activity}"
            )

    except FileNotFoundError:
        print("Protoss database not found. Have you run any coordinations?")
    except Exception as e:
        print(f"Error: {e}")


@app.command()
def logs(
    coordination_id: str = typer.Argument(..., help="Coordination ID to show logs for"),
):
    """Show message logs for a coordination session."""
    inspector = ProtossInspector()
    try:
        messages = inspector.get_messages(coordination_id)
        if not messages:
            print(f"No messages found for coordination {coordination_id}")
            return

        print(f"Messages for coordination {coordination_id}:")
        print("-" * 80)

        for msg in messages:
            timestamp = (
                msg.timestamp.split(".")[0] if "." in msg.timestamp else msg.timestamp
            )
            print(f"[{timestamp}] {msg.sender}: {msg.content}")

    except FileNotFoundError:
        print("Protoss database not found. Have you run any coordinations?")
    except Exception as e:
        print(f"Error: {e}")


@app.command()
def check(coordination_id: str = typer.Argument(..., help="Coordination ID to check")):
    """Check if a coordination is complete."""
    inspector = ProtossInspector()
    try:
        is_complete = inspector.is_complete(coordination_id)
        status = inspector.get_coordination_status(coordination_id)

        if not status:
            print(f"Coordination {coordination_id} not found.")
            return

        print(f"Coordination {coordination_id}:")
        print(f"  Complete: {'✓' if is_complete else '✗'}")
        print(f"  Messages: {status.message_count}")
        print(
            f"  Agents: {', '.join(status.active_agents) if status.active_agents else 'None'}"
        )
        print(f"  Last Activity: {status.last_activity}")

    except FileNotFoundError:
        print("Protoss database not found. Have you run any coordinations?")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """CLI entry point for pyenv/pip installations."""
    app()
