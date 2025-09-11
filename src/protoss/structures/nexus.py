"""Nexus: Human command center for Protoss swarms."""

import sys
import asyncio
import websockets
from .pylon import Pylon
from .gateway import Gateway
from ..khala import Psi
from ..constants import PYLON_DEFAULT_PORT


class Nexus:
    """Human command center. Start grid, spawn Carrier, interface with swarm."""

    def __init__(self, port: int = PYLON_DEFAULT_PORT):
        self.port = port
        self.pylon = None
        self.gateway = None

    async def start_grid(self):
        """Start Pylon coordination grid."""
        self.pylon = Pylon(self.port)
        print(f"⚡ Starting Protoss grid on port {self.port}")
        await self.pylon.start()
        print("🔹 Grid active. Press Ctrl+C to stop.")
        
        try:
            await asyncio.Future()  # Wait indefinitely
        except KeyboardInterrupt:
            print("\n⚡ Stopping Protoss grid...")
            await self.pylon.stop()
            print("🔹 Grid offline")

    async def spawn_carrier(self):
        """Launch persistent Carrier for human interface."""
        if not self.gateway:
            self.gateway = Gateway()
        
        print("🛸 Carrier has arrived...")
        
        try:
            carrier_id = await self.gateway.spawn_carrier(
                "Initialize human-swarm coordination interface",
                "nexus"
            )
            print(f"⚡ All paths are one - {carrier_id} operational")
            print("🎯 Ready for conversational coordination commands")
        except Exception as e:
            print(f"❌ Carrier spawn failed: {e}")
            print("🔹 Ensure Pylon grid is running: protoss start")

    async def carrier_interface(self, command: str):
        """Conversational interface to Carrier. Auto-spawns on first use."""
        print(f"🛸 Processing: {command}")
        
        try:
            # Auto-spawn Carrier if not already active
            if not self.gateway:
                self.gateway = Gateway()
            
            # Check if Carrier exists, spawn if needed
            try:
                client_id = "nexus"
                uri = f"ws://localhost:{self.port}/{client_id}"
                
                async with websockets.connect(uri) as websocket:
                    # Try to ping existing Carrier
                    ping = f"§PSI:carrier:{client_id}:ping:"
                    await websocket.send(ping)
                    
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    except asyncio.TimeoutError:
                        # No Carrier, spawn one
                        print("🛸 Carrier has arrived...")
                        # Start Carrier in background task instead of blocking
                        asyncio.create_task(self.gateway.spawn_carrier(
                            "Initialize human-swarm coordination interface",
                            "nexus"
                        ))
                        await asyncio.sleep(3)  # Give Carrier time to initialize
            except:
                # Carrier spawn failed or connection issues - will be caught below
                pass
            
            # Send command to Carrier
            async with websockets.connect(f"ws://localhost:{self.port}/nexus") as websocket:
                request = f"§PSI:carrier:nexus:command:{command}"
                await websocket.send(request)
                
                response = await websocket.recv()
                psi = Psi.parse(response)
                
                if psi and psi.type == "response":
                    print(f"🛸 Carrier: {psi.content}")
                else:
                    print("❌ No response from Carrier")
                    
        except ConnectionRefusedError:
            print("❌ No Pylon grid running")
            print("💡 Start infrastructure: protoss start")
        except Exception as e:
            print(f"❌ Communication failed: {e}")

    def cli(self):
        """CLI entry point."""
        
        # Help
        if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) == 1:
            print("⚡ Protoss - AI Agent Coordination Grid")
            print()
            print("🔧 CONTROL:")
            print("  protoss start [port]              # Start Pylon grid")
            print("  protoss stop                      # Shutdown grid")
            print()
            print("🛸 COORDINATION:")
            print('  protoss "build tokenizer"         # Auto-spawn Carrier, natural coordination')
            print('  protoss "should we use React?"    # Carrier routes to Sacred Four internally')
            print('  protoss "coordinate 5 agents"     # Carrier deploys squad internally')
            return

        # Start grid
        if len(sys.argv) > 1 and sys.argv[1] == "start":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else PYLON_DEFAULT_PORT
            nexus = Nexus(port)
            asyncio.run(nexus.start_grid())
            return

        # Stop grid
        if len(sys.argv) > 1 and sys.argv[1] == "stop":
            print("⚡ Stopping Protoss grid...")
            print("🔹 Grid offline. En Taro Adun!")
            return

        # Remove direct conclave access - Carrier handles Sacred Four routing

        # Conversational interface - any unrecognized command
        if len(sys.argv) > 1 and sys.argv[1] not in ["start", "stop"]:
            full_command = " ".join(sys.argv[1:])
            nexus = Nexus()
            asyncio.run(nexus.carrier_interface(full_command))
            return

        # Default: unknown command
        print(f"❌ Unknown command: {' '.join(sys.argv[1:])}")
        print("💡 Run 'protoss --help' for usage information")


def main():
    """CLI entry point."""
    nexus = Nexus()
    nexus.cli()


if __name__ == "__main__":
    main()