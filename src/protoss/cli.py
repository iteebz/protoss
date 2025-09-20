"""Protoss CLI interface."""

import asyncio
import typer

from .core import Protoss

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
    rich_context: bool = typer.Option(True, "--rich/--simple", help="Use archon context seeding"),
    max_agents: int = typer.Option(50, "--max-agents", help="Maximum agents allowed"),
):
    """Coordinate agents on task with real-time updates."""
    
    async def run_coordination():
        protoss = Protoss(
            agents=agents,
            max_agents=max_agents,
            timeout=timeout,
            debug=debug,
            rich_context=rich_context
        )
        
        print(f"🔮 Protoss coordination starting...")
        print(f"📋 Task: {task}")
        print(f"⚔️ Agents: {agents}")
        print()
        
        try:
            async for event in protoss(task):
                if event.type == "coordination_start":
                    print(f"🚀 {event.content}")
                elif event.type == "context_seeding":
                    print(f"🌱 {event.content}")
                elif event.type == "coordination_complete":
                    print(f"✅ {event.content}")
                elif event.type == "coordination_timeout":
                    print(f"⏰ {event.content}")
                elif event.type == "coordination_error":
                    print(f"❌ {event.content}")
                    
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
        protoss = Protoss()
        status = await protoss.status()
        
        print("🔮 Protoss Status")
        print(f"Status: {status['status']}")
        
        if status['status'] == 'online':
            print(f"Active pathways: {status['active_pathways']}")
            print(f"Khala connections: {status['khala']['minds']}")
            print(f"Total memories: {status['khala']['memories']}")
            
            if status['recent_pathways']:
                print("\nRecent pathways:")
                for pathway in status['recent_pathways']:
                    print(f"  - {pathway['name']}: {pathway['memories']} messages")
    
    asyncio.run(show_status())


@app.command()
def config():
    """Show default configuration."""
    from .config import Config
    
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