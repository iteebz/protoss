"""Nexus: Pure infrastructure management for Protoss coordination."""

import sys
import asyncio
import websockets
from .pylon import Pylon
from .gateway import Gateway
from ..khala import Khala
from ..conclave import Conclave
from ..units.archon import Archon
from ..units.carrier import Carrier
from ..constants import PYLON_DEFAULT_PORT


class Nexus:
    """Pure infrastructure hub. Manages all Protoss coordination infrastructure."""

    def __init__(self, port: int = PYLON_DEFAULT_PORT):
        self.port = port
        self._shutdown_event = asyncio.Event()
        
        # Infrastructure components
        self.pylon = None
        self.gateway = None
        self.khala = None
        self.conclave = None
        self.archon = None
        self.carrier = None

    async def initialize_infrastructure(self):
        """Initialize all Protoss coordination infrastructure."""
        print(f"⚡ Initializing Protoss infrastructure on port {self.port}")
        
        # Core infrastructure - Khala discovers the grid
        self.khala = Khala()
        self.khala.set_grid_port(self.port)  # Set singleton grid port
        self.pylon = Pylon(self.port)
        self.gateway = Gateway()
        self.conclave = Conclave()  # No port needed - uses singleton Khala
        self.archon = Archon()
        
        # Start Pylon grid
        await self.pylon.start()
        print("🔹 Pylon grid online")
        
        # Initialize Carrier via Gateway factory
        self.carrier = self.gateway._create_unit("carrier")
        
        print("🛸 Carrier initialized with service discovery")
        print("🔹 All infrastructure online - ready for coordination")

    async def start_grid(self):
        """Start complete Protoss coordination infrastructure."""
        await self.initialize_infrastructure()
        
        print("🔹 Infrastructure running. Press Ctrl+C to stop.")
        try:
            await self._shutdown_event.wait()  # Wait for shutdown signal
        except KeyboardInterrupt:
            print("\n⚡ Stopping Protoss infrastructure...")
        finally:
            await self.shutdown_infrastructure()
            print("🔹 Infrastructure offline")

    async def shutdown_infrastructure(self):
        """Gracefully shutdown all infrastructure."""
        self._shutdown_event.set()  # Signal shutdown
        if self.carrier:
            await self.carrier.despawn()
        if self.pylon:
            await self.pylon.stop()

    async def spawn_carrier(self):
        """Deploy Carrier using existing infrastructure."""
        if not self.carrier:
            await self.initialize_infrastructure()
        
        print("🛸 Carrier deploying...")
        
        try:
            await self.carrier.connect_to_khala()
            print(f"⚡ {self.carrier.id} operational")
            print("🎯 Ready for conversational coordination commands")
        except Exception as e:
            print(f"❌ Carrier deployment failed: {e}")
            print("🔹 Ensure infrastructure is running: protoss start")

    async def carrier_interface(self, command: str):
        """Clean conversational interface to Carrier using infrastructure."""
        if not self.carrier:
            await self.initialize_infrastructure()
        
        try:
            response = await self.carrier.process_command(command)
            print(f"🛸 Carrier: {response}")
        except Exception as e:
            print(f"❌ Carrier interface failed: {e}")
            print("💡 Ensure infrastructure is running: protoss start")

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