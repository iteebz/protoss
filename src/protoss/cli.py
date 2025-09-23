"""Protoss CLI interface."""

import asyncio
import os
import subprocess
import signal
import sys
import typer

from protoss import Protoss

from .core.config import Config
from .core.khala import Khala


app = typer.Typer(
    help="""Constitutional AI coordination through emergent agent swarms.

Usage: protoss \"constitutional vision\"
Pure constitutional emergence - no ceremony required."""
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


@app.command()
def coordinate(
    vision: str = typer.Argument(..., help="Constitutional vision to manifest"),
    port: int = typer.Option(8888, "--port", "-p", help="Bus port"),
    timeout: int = typer.Option(3600, "--timeout", "-t", help="Timeout in seconds"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
    max_agents: int = typer.Option(
        100, "--max-agents", "-m", help="Max agents for coordination"
    ),
):
    """Constitutional coordination through pure emergence."""

    async def run_coordination():
        try:
            async with Protoss(
                vision,
                port=port,
                timeout=timeout,
                debug=debug,
                max_agents=max_agents,
            ) as swarm:
                result = await swarm
                print("Constitutional emergence complete!")
                print()
                print(result)

        except KeyboardInterrupt:
            print("\nCoordination interrupted by user")
        except Exception as e:
            print(f"Coordination failed: {e}")
            if debug:
                import traceback

                traceback.print_exc()

    asyncio.run(run_coordination())


@app.command()
def status():
    """Show Protoss coordination system status."""

    async def show_status():
        config = Config()
        khala = Khala(bus_url=config.bus_url)
        try:
            await khala.connect(client_id="status_client")
            await khala.send(content="", msg_type="status_req")

            response_message = await khala.receive()
            if response_message and response_message.msg_type == "status_resp":
                status_data = (
                    response_message.event
                )  # Assuming event contains the status dict

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
        bus_process = subprocess.Popen(
            ["python", "-m", "src.protoss.cli", "bus", f"--port={port}"]
        )
        with open(BUS_PID_FILE, "w") as f:
            f.write(str(bus_process.pid))
        print(f"Bus started with PID {bus_process.pid}")

        print("Protoss infrastructure is running. Press Ctrl+C to stop.")

        def signal_handler(sig, frame):
            print("\nStopping Protoss infrastructure...")
            stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()

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
            import uuid

            current_channel_id = f"ask-{uuid.uuid4().hex[:8]}"
        else:
            current_channel_id = channel_id

        print(f"Asking swarm in channel {current_channel_id}...")

        try:
            await khala.connect(client_id="human_asker")
            # Send the initial question, which implicitly joins the channel
            await khala.send(
                content=f"{question} @arbiter",
                channel=current_channel_id,
                sender="human",
            )
            print(f"Human: {question}")

            print("Waiting for Arbiter's response...")
            async for message in khala.listen():
                if (
                    message
                    and message.msg_type == "event"
                    and message.channel == current_channel_id
                ):
                    sender = message.sender
                    content = message.event.get("content")

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


def main():
    """CLI entry point."""
    try:
        app()
    except Exception as e:
        print(f"CLI Error: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
