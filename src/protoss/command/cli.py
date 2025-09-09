"""CLI interface for Protoss coordination system."""

import sys
import asyncio
import json


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


async def _spawn_carrier():
    """Launch persistent Carrier for human interface."""
    from ..structures.gateway import Gateway
    from ..constants import PYLON_DEFAULT_PORT
    
    print("🛸 Carrier has arrived...")
    
    try:
        gateway = Gateway()
        carrier_id = await gateway.spawn_carrier(
            "Initialize human-swarm coordination interface",
            "nexus"  # Report to command
        )
        print(f"⚡ All paths are one - {carrier_id} operational")
        print("🎯 Ready for conversational coordination commands")
        
    except Exception as e:
        print(f"❌ Carrier spawn failed: {e}")
        print("🔹 Ensure Pylon grid is running: protoss start")


async def _carrier_interface(command: str):
    """Conversational interface to Carrier."""
    from .observatory import PylonClient
    
    print(f"🛸 Processing: {command}")
    
    try:
        client = PylonClient()
        # Send command to active Carrier via Khala
        result = await client._request(f"carrier_command:{command}")
        
        if "error" in result:
            print(f"❌ {result['error']}")
            if "No Pylon grid" in result['error']:
                print("💡 Start infrastructure: protoss start")
                print("💡 Spawn Carrier: protoss carrier spawn")
        else:
            # Display Carrier response
            response = result.get("response", "No response from Carrier")
            print(f"🛸 Carrier: {response}")
            
    except Exception as e:
        print(f"❌ Communication failed: {e}")


async def _carrier_status():
    """Get Carrier coordination status."""
    from .observatory import PylonClient
    
    try:
        client = PylonClient()
        result = await client._request("carrier_status")
        
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            status = result.get("status", {})
            print("🛸 Carrier Status")
            print(f"  Active Interceptors: {status.get('active_interceptors', 0)}")
            print(f"  Context Buffer: {status.get('context_buffer_size', 0)} items")
            print(f"  Coordination: {status.get('coordination_capacity', 'unknown')}")
            print(f"  Health: {status.get('health', 'unknown')}")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")


async def _stop_carrier():
    """Despawn Carrier."""
    from .observatory import PylonClient
    
    try:
        client = PylonClient()
        result = await client._request("carrier_stop")
        
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print("🛸 Carrier departing...")
            print("⚡ En Taro Adun!")
            
    except Exception as e:
        print(f"❌ Carrier stop failed: {e}")


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
        print("🛸 CARRIER:")
        print('  protoss "<command>"               # Conversational human interface')
        print("  protoss carrier spawn             # Launch persistent Carrier")
        print("  protoss carrier status            # Carrier coordination status")
        print("  protoss carrier stop              # Despawn Carrier")
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

    # Carrier commands
    if len(sys.argv) > 1 and sys.argv[1] == "carrier":
        if len(sys.argv) > 2:
            if sys.argv[2] == "spawn":
                asyncio.run(_spawn_carrier())
                return
            elif sys.argv[2] == "status":
                asyncio.run(_carrier_status())
                return
            elif sys.argv[2] == "stop":
                asyncio.run(_stop_carrier())
                return
        
        # Default carrier help
        print("🛸 Carrier Commands:")
        print("  protoss carrier spawn    # Launch persistent Carrier")
        print("  protoss carrier status   # Coordination status") 
        print("  protoss carrier stop     # Despawn Carrier")
        return

    # Start grid
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        from ..constants import PYLON_DEFAULT_PORT
        port = int(sys.argv[2]) if len(sys.argv) > 2 else PYLON_DEFAULT_PORT
        
        asyncio.run(_start_grid(port))
        return

    # Conversational interface - detect quoted commands
    if len(sys.argv) > 1 and sys.argv[1].startswith('"') and sys.argv[-1].endswith('"'):
        # Join all args and strip quotes for full command
        full_command = " ".join(sys.argv[1:]).strip('"')
        asyncio.run(_carrier_interface(full_command))
        return

    # Default: show help
    main()


if __name__ == "__main__":
    main()
