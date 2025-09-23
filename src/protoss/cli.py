"""Protoss CLI interface."""

import asyncio
import os
import subprocess
import signal
import sys
import typer

from typing import Optional
from uuid import uuid4
from protoss import Protoss

from .core.config import Config
from .core.khala import Khala


app = typer.Typer(
    help="AI coordination through emergent agent swarms.", no_args_is_help=True
)


@app.command()
def bus(
    port: int = typer.Option(8888, "--port", "-p", help="Port to run the Bus on"),
    max_agents: int = typer.Option(
        100, "--max-agents", "-m", help="Max agents per channel"
    ),
):
    """Start the unified Protoss Bus as a standalone process."""
    from .core.bus import main as bus_main

    print(f"Starting unified Protoss Bus on port {port}...")

    sys.argv = ["protoss-bus", f"--port={port}", f"--max-agents={max_agents}"]
    bus_main()


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
def status():
    """Show Protoss coordination system status."""

    async def show_status():
        config = Config()
        khala = Khala(bus_url=config.bus_url)
        try:
            await khala.connect(client_id="status_client")
            await khala.send(
                channel="system", sender="status_client", event_type="status_req"
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


PROTOSS_DIR = ".protoss"
BUS_PID_FILE = f"{PROTOSS_DIR}/bus.pid"


def _ensure_protoss_dir():
    os.makedirs(PROTOSS_DIR, exist_ok=True)


@app.command()
def start(
    port: int = typer.Option(8888, "--port", "-p", help="Port to run the Bus on"),
    max_agents: int = typer.Option(
        100, "--max-agents", "-m", help="Max agents per channel"
    ),
):
    """Start the Protoss Bus and Gateway as background daemons."""
    _ensure_protoss_dir()

    try:
        log_file = open(f"{PROTOSS_DIR}/bus.log", "a")
        bus_process = subprocess.Popen(
            ["python", "-m", "src.protoss.cli", "bus", f"--port={port}"],
            stdout=log_file,
            stderr=log_file,
        )
        with open(BUS_PID_FILE, "w") as f:
            f.write(str(bus_process.pid))
        print(f"Bus started with PID {bus_process.pid}")

        print("Protoss infrastructure is running.")

    except Exception as e:
        print(f"Failed to start Protoss infrastructure: {e}")
        stop()


def _stop_process(name: str, pid_file: str):
    """Helper to stop a single daemon process."""
    if not os.path.exists(pid_file):
        return

    try:
        with open(pid_file, "r") as f:
            pid = int(f.read())

        try:
            os.kill(pid, signal.SIGTERM)
            print(f"{name} (PID {pid}) stopped.")
        except ProcessLookupError:
            print(f"{name} (PID {pid}) was not running.")

    except (IOError, ValueError) as e:
        print(f"Could not read PID file {pid_file}: {e}")
    finally:
        if os.path.exists(pid_file):
            os.remove(pid_file)


@app.command()
def stop():
    """Stop the Protoss Bus daemon."""
    _stop_process("Protoss Bus", BUS_PID_FILE)


@app.command()
def monitor(
    port: int = typer.Option(
        8888, "--port", "-p", help="Port of the Bus to connect to"
    ),
):
    """Live monitor for the swarm."""
    from .clients.monitor import MonitorApp

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
            from protoss.lib.channels import query_channel

            ask_channel_id = query_channel()
        else:
            ask_channel_id = channel_id

        print(f"Asking swarm in channel {ask_channel_id}...")

        # Generate a coordination_id for the ask command
        ask_coordination_id = str(uuid4())

        try:
            await khala.connect(client_id="human_asker")
            # Send the initial question, which implicitly joins the channel
            await khala.send(
                content=f"{question} @arbiter",
                channel=ask_channel_id,
                sender="human",
                coordination_id=ask_coordination_id,  # Use the generated ID
                event_type="human_ask",
            )
            print(f"Human: {question}")

            print("Waiting for Arbiter's response...")
            async for event in khala.listen():  # Listen for structured events
                if (
                    event
                    and event.get("type") == "agent_message"
                    and event.get("channel") == ask_channel_id
                ):
                    sender = event.get("sender")
                    content = event.get("message", {}).get(
                        "content"
                    )  # Extract content from message sub-dict

                    if sender and sender.startswith("arbiter-"):
                        print(f"\nARBITER: {content}")
                        break
                    elif (
                        sender == "system" and "has joined the coordination" in content
                    ):
                        pass
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
