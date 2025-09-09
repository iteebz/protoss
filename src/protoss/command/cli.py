"""CLI interface for Protoss coordination system."""

import sys
import asyncio


async def _start_grid(port: int):
    """Start Pylon coordination grid."""
    from ..structures.pylon import Pylon
    
    pylon = Pylon(port)

    print(f"⚡ Starting Protoss grid on port {port}")
    await pylon.start()
    print("🔹 Grid active. Press Ctrl+C to stop.")

    try:
        # Keep running until interrupted
        await asyncio.Future()  # Wait indefinitely
    except KeyboardInterrupt:
        print("\n⚡ Stopping Protoss grid...")
        await pylon.stop()
        print("🔹 Grid offline")


def main():
    """CLI entry point."""

    # Help
    if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) == 1:
        print("⚡ Protoss - AI Agent Coordination Grid")
        print()
        print("📊 INSPECTION:")
        print("  protoss status                    # System overview")
        print("  protoss pathways                  # List Khala pathways")
        print("  protoss minds                     # List connected minds")
        print("  protoss pathway <name>            # Pathway details")
        print()
        print("🔧 CONTROL:")
        print("  protoss start [port]              # Start Pylon grid")
        print("  protoss stop                      # Stop grid")
        print()
        print("🧠 CONCLAVE:")
        print(
            '  protoss conclave "<question>"     # Summon the Conclave for deliberation'
        )
        print()
        print("🚀 TESTING:")
        print("  protoss send <pathway> <message>  # Send test message")
        print("  protoss spawn <mind_id>           # Spawn test mind")
        return

    # Status
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        from .observatory import observe

        observe()
        return

    # Pathways
    if len(sys.argv) > 1 and sys.argv[1] == "pathways":
        from .observatory import show_pathways

        show_pathways()
        return

    # Minds
    if len(sys.argv) > 1 and sys.argv[1] == "minds":
        from .observatory import show_minds

        show_minds()
        return

    # Pathway details
    if len(sys.argv) > 2 and sys.argv[1] == "pathway":
        from .observatory import show_pathway

        show_pathway(sys.argv[2])
        return

    # Conclave deliberation
    if len(sys.argv) > 2 and sys.argv[1] == "conclave":
        question = " ".join(sys.argv[2:])
        from ..conclave import deliberate

        deliberate(question)
        return

    # Start grid
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        from ..constants import PYLON_DEFAULT_PORT
        port = int(sys.argv[2]) if len(sys.argv) > 2 else PYLON_DEFAULT_PORT
        
        asyncio.run(_start_grid(port))
        return

    # Default: show help
    main()


if __name__ == "__main__":
    main()
