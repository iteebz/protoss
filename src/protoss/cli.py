"""Protoss CLI interface."""

import asyncio
import typer

from .core import Protoss
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
        config = Config(
            agents=agents,
            max_agents=max_agents,
            timeout=timeout,
            debug=debug,
            rich_context=rich_context,
        )
        protoss = Protoss(config)

        print("🔮 Protoss coordination starting...")
        print(f"📋 Task: {task}")
        print(f"⚔️ Agents: {agents}")
        print()

        try:
            result = await protoss(task)
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
        config = Config()  # Use default config
        protoss = Protoss(config)
        status = await protoss.status()

        print("🔮 Protoss Status")
        print(f"Status: {status['status']}")

        if status["status"] == "online":
            print(f"Active channels: {status['active_channels']}")
            if status.get("bus"):
                bus_snapshot = status["bus"]
                print(
                    "Bus metrics: "
                    f"channels={bus_snapshot.get('channels', 0)} "
                    f"agents={bus_snapshot.get('agents', 0)} "
                    f"memories={bus_snapshot.get('memories', 0)}"
                )

            if status.get("recent_channels"):
                print("\nRecent channels:")
                for channel in status["recent_channels"]:
                    name = channel.get("name", "<unknown>")
                    agents = channel.get("agents", 0)
                    memories = channel.get("memories", 0)
                    recent = channel.get("recent")
                    recent_preview = (
                        f" - recent: {recent[:60]}..." if isinstance(recent, str) and recent else ""
                    )
                    print(
                        f"  - {name} (agents={agents}, memories={memories}){recent_preview}"
                    )

    asyncio.run(show_status())


@app.command()
def config():
    """Show default configuration."""
    from .core.config import Config

    default_config = Config()

    print("🔮 Protoss Default Configuration")
    print(f"Agents: {default_config.agents}")
    print(f"Max agents: {default_config.max_agents}")
    print(f"Timeout: {default_config.timeout}s")
    print(f"LLM: {default_config.llm}")
    print(f"Archives: {default_config.archives}")
    print(f"Rich context: {default_config.rich_context}")
    print(f"Debug: {default_config.debug}")


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
