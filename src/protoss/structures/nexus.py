"""Nexus: Pure infrastructure management for Protoss coordination."""

import sys
import asyncio
import websockets
from .pylon import Pylon
from .gateway import Gateway
from ..khala import khala
from ..conclave import Conclave
from ..units.archon import Archon
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

    async def build_base(self):
        """Build all Protoss coordination infrastructure."""
        print(f"⚡ Initializing Protoss infrastructure on port {self.port}")
        
        # Core infrastructure - Khala discovers the grid
        self.khala = khala
        self.khala.set_grid_port(self.port)  # Set singleton grid port
        self.pylon = Pylon(self.port)
        self.gateway = Gateway()
        self.conclave = Conclave()  # No port needed - uses singleton Khala
        self.archon = Archon()
        
        # Start Pylon grid
        await self.pylon.start()
        print("🔹 Pylon grid online")
        
        print("🔹 All infrastructure online - ready for coordination")

    async def start_grid(self):
        """Start complete Protoss coordination infrastructure."""
        await self.build_base()
        
        print("🔹 Infrastructure running. Ready for coordination.")
        print("💡 Run 'protoss stop' to shutdown.")

    async def shutdown_infrastructure(self):
        """Gracefully shutdown all infrastructure."""
        self._shutdown_event.set()  # Signal shutdown
        if self.pylon:
            await self.pylon.stop()


    def cli(self):
        """CLI entry point."""
        
        # Help
        if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) == 1:
            print("⚡ Protoss - AI Agent Coordination Grid")
            print()
            print("🔧 CONTROL:")
            print("  protoss start [port]              # Start Pylon grid")
            print("  protoss stop                      # Shutdown grid")
            print("  protoss nuke                      # Delete .protoss directory")
            print()
            print("🛸 COORDINATION:")
            print('  protoss "coordinate feature X"   # Primary executor interface')
            print('  protoss status                   # Infrastructure and swarm state')
            print('  protoss spawn zealot "task"      # Direct unit spawning')
            print('  protoss warp squad "task"        # Multi-unit coordination')
            print('  protoss monitor                  # Real-time Khala stream')
            print('  protoss conclave "strategy Q"    # Direct Sacred Four access')
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

        # Nuke .protoss directory
        if len(sys.argv) > 1 and sys.argv[1] == "nuke":
            import shutil
            from pathlib import Path
            protoss_dir = Path(".protoss")
            if protoss_dir.exists():
                shutil.rmtree(protoss_dir)
                print("💥 .protoss directory nuked")
                print("🔹 Clean slate ready. En Taro Adun!")
            else:
                print("💥 No .protoss directory found")
            return

        # Executor atomic coordination - primary human interface
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in ["start", "stop", "nuke", "status", "spawn", "warp", "monitor", "conclave"]:
            message = " ".join(sys.argv[1:])
            nexus = Nexus()
            asyncio.run(nexus._executor_coordinate(message))
            return
            
        # Status check
        if len(sys.argv) > 1 and sys.argv[1] == "status":
            nexus = Nexus()
            asyncio.run(nexus._status())
            return
            
        # Spawn unit  
        if len(sys.argv) > 3 and sys.argv[1] == "spawn":
            unit_type = sys.argv[2]
            task = " ".join(sys.argv[3:])
            nexus = Nexus()
            asyncio.run(nexus._spawn_unit(unit_type, task))
            return
            
        # Warp squad
        if len(sys.argv) > 3 and sys.argv[1] == "warp":
            squad_type = sys.argv[2] 
            task = " ".join(sys.argv[3:])
            nexus = Nexus()
            asyncio.run(nexus._warp_squad(squad_type, task))
            return
            
        # Monitor Khala stream
        if len(sys.argv) > 1 and sys.argv[1] == "monitor":
            nexus = Nexus()
            asyncio.run(nexus._monitor())
            return
            
        # Conclave direct access
        if len(sys.argv) > 2 and sys.argv[1] == "conclave":
            question = " ".join(sys.argv[2:])
            nexus = Nexus()
            asyncio.run(nexus._conclave_direct(question))
            return

        # Default: unknown command
        print(f"❌ Unknown command: {' '.join(sys.argv[1:])}")
        print("💡 Run 'protoss --help' for usage information")

    async def _conclave_direct(self, question: str):
        """Direct Sacred Four access."""
        if not self.conclave:
            await self.build_base()
        
        try:
            guidance = await self.conclave.convene(question)
            print(f"🏛️ Sacred Four Guidance:\n{guidance}")
        except Exception as e:
            print(f"❌ Conclave access failed: {e}")
            print("💡 Ensure infrastructure is running: protoss start")

    async def _status(self):
        """Show infrastructure and swarm state."""
        print("⚡ PROTOSS INFRASTRUCTURE STATUS")
        print()
        
        try:
            # Check infrastructure components
            if not self.khala:
                await self.build_base()
                
            # Khala status
            khala_status = self.khala.status
            print(f"🔮 KHALA: {khala_status['pathways']} pathways, {khala_status['total_minds']} minds, {khala_status['total_memories']} memories")
            
            # Show active pathways
            pathways = await self.khala.pathways()
            if pathways:
                print("\n📡 ACTIVE PATHWAYS:")
                for pathway in pathways[:5]:  # Show top 5
                    print(f"  🌐 {pathway['name']}: {pathway['minds']} minds, {pathway['memories']} memories")
                if len(pathways) > 5:
                    print(f"  ... and {len(pathways) - 5} more pathways")
            else:
                print("\n📡 No active pathways")
                
            # Show connected minds  
            minds = self.khala.minds
            if minds:
                print(f"\n⚔️ CONNECTED UNITS: {len(minds)} total")
                for mind in minds[:3]:  # Show top 3
                    print(f"  🔹 {mind['id']}: {mind['pathway_count']} pathways")
                if len(minds) > 3:
                    print(f"  ... and {len(minds) - 3} more units")
            else:
                print("\n⚔️ No units currently connected")
                
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            print("💡 Try: protoss start")
            
    async def _spawn_unit(self, unit_type: str, task: str):
        """Spawn single unit with task."""
        print(f"🌀 Spawning {unit_type} for task: {task[:50]}...")
        
        try:
            if not self.gateway:
                await self.build_base()
                
            # Spawn unit via Gateway
            unit = self.gateway.spawn(unit_type)
            pathway = f"mission-{unit.id}"
            
            # Execute task on pathway
            await unit.execute(task, pathway)
            print(f"⚔️ {unit.id} deployed to pathway: {pathway}")
            
        except Exception as e:
            print(f"❌ Unit spawn failed: {e}")
            print("💡 Ensure infrastructure is running: protoss start")
            
    async def _warp_squad(self, squad_type: str, task: str):
        """Multi-unit coordination via Gateway.warp()."""
        print(f"🔥 Warping {squad_type} for task: {task[:50]}...")
        
        try:
            if not self.gateway:
                await self.build_base()
                
            # Define squad compositions
            squad_types = {
                "squad": ["zealot", "zealot", "stalker"],  # Basic squad
                "research": ["zealot", "zealot", "archon"], # Research team
                "quality": ["zealot", "stalker", "stalker"], # Quality focus
            }
            
            units = squad_types.get(squad_type, ["zealot", "zealot"])
            squad_id = await self.gateway.warp(task, units)
            print(f"⚔️ Squad operational: {squad_id}")
            
        except Exception as e:
            print(f"❌ Squad warp failed: {e}")
            print("💡 Ensure infrastructure is running: protoss start")
            
    async def _monitor(self):
        """Show recent Khala consciousness activity."""
        print("📡 KHALA CONSCIOUSNESS STREAM")
        print()
        
        try:
            if not self.khala:
                await self.build_base()
                
            # Show recent activity across all pathways
            pathways = await self.khala.pathways()
            if pathways:
                print("🌐 RECENT PATHWAY ACTIVITY:")
                for pathway in pathways:
                    print(f"\n  📡 {pathway['name']} ({pathway['memories']} messages)")
                    
                    # Show last 3 messages from each pathway
                    recent_messages = await self.khala.recent_messages(pathway['name'])
                    if recent_messages:
                        for message in recent_messages[-3:]:  # Last 3
                            print(f"    ⚡ {message[:70]}...")
                    else:
                        print("    💭 No recent messages")
            else:
                print("📡 No pathway activity detected")
                print("💡 Try: protoss spawn zealot \"hello world\"")
                
        except Exception as e:
            print(f"❌ Monitor failed: {e}")
            print("💡 Ensure infrastructure is running: protoss start")
            
    async def _executor_coordinate(self, message: str):
        """Executor atomic coordination - primary human interface."""
        print(f"🎯 Executor coordinating: {message[:70]}...")
        
        try:
            if not self.gateway:
                await self.build_base()
                
            # Spawn executor and execute coordination
            from ..units.executor import Executor
            executor = Executor()
            
            # Execute with conversation persistence 
            await executor.coordinate(message)
            print("⚔️ Coordination complete")
            
        except Exception as e:
            print(f"❌ Executor coordination failed: {e}")
            print("💡 Ensure infrastructure is running: protoss start")


def main():
    """CLI entry point."""
    nexus = Nexus()
    nexus.cli()


if __name__ == "__main__":
    main()