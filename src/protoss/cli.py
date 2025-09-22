"""Protoss CLI interface."""

import asyncio
import json
import typer
import websockets

from protoss import protoss
from .core.config import Config


app = typer.Typer(
    help="""Constitutional AI coordination through emergent agent swarms.

Direct usage: protoss "task description" --agents 5
Event streaming shows real-time coordination progress."""
)


@app.command()
def coordinate(
    task: str = typer.Argument(..., help="Coordination task description"),
    agents: int = typer.Option(5, "--agents", "-a", help="Number of agents"),
    timeout: int = typer.Option(3600, "--timeout", "-t", help="Timeout in seconds"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
    rich_context: bool = typer.Option(
        True, "--rich/--simple", help="Use archon context seeding"
    ),
    max_agents: int = typer.Option(50, "--max-agents", help="Maximum agents allowed"),
):
    """Coordinate agents on task with real-time updates."""

    async def run_coordination():
        try:
            async with protoss(
                task,
                agents=agents,
                max_agents=max_agents,
                timeout=timeout,
                debug=debug,
                rich_context=rich_context,
            ) as swarm:
                result = await swarm._await_completion()
                print("✅ Coordination completed successfully!")
                print()
                print(result)

        except KeyboardInterrupt:
            print("\n🛑 Coordination interrupted by user")
        except Exception as e:
            print(f"❌ Coordination failed: {e}")
            if debug:
                import traceback

                traceback.print_exc()

    asyncio.run(run_coordination())


@app.command()
def status():
    """Show Protoss coordination system status."""

    async def show_status():
        config = Config()
        uri = f"{config.bus_url}/status_client"
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({"type": "status_req"}))
                response = await websocket.recv()
                status_data = json.loads(response)

                print("🔮 Protoss Status")
                print(f"Status: {status_data.get('status', 'unknown')}")

                if status_data.get("status") == "online":
                    bus_snapshot = status_data.get("bus", {})
                    print(
                        "Bus metrics: "
                        f"channels={bus_snapshot.get('channels', 0)} "
                        f"agents={bus_snapshot.get('agents', 0)} "
                        f"messages={bus_snapshot.get('messages', 0)}"
                    )

        except (ConnectionRefusedError, websockets.exceptions.InvalidURI, websockets.exceptions.InvalidHandshake):
            print("Could not connect to Protoss Bus. Is it running?")
        except Exception as e:
            print(f"An error occurred: {e}")


    asyncio.run(show_status())


@app.command()
def monitor():
    """Monitor the Protoss Bus in real-time."""

    async def run_monitor():
        config = Config()
        uri = f"{config.bus_url}/cli_monitor"
        print(f"👁️  Connecting to Protoss Bus at {uri}...")
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({"type": "monitor_req"}))
                response = await websocket.recv()
                if json.loads(response).get("status") != "monitoring":
                    print("❌ Failed to subscribe to monitor stream.")
                    return
                
                print("✅ Connected. Monitoring swarm activity...")
                async for message in websocket:
                    data = json.loads(message)
                    channel = data.get("channel", "unknown")
                    sender = data.get("sender", "unknown")
                    content = data.get("content", "")
                    
                    # Simple formatting
                    print(f"[{channel}] {sender}: {content}")

        except (ConnectionRefusedError, websockets.exceptions.InvalidURI, websockets.exceptions.InvalidHandshake):
            print("Could not connect to Protoss Bus. Is it running?")
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user.")
        except Exception as e:
            print(f"An error occurred: {e}")

    asyncio.run(run_monitor())


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
