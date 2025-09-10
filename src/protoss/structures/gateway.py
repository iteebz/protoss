"""Gateway: Zealot spawning facility.

Spawns Cogency agents, connects to Pylon, executes task, despawns.
"""

import uuid
import asyncio
import websockets
from cogency import Agent
from ..units import Zealot, Tassadar, Zeratul, Artanis, Fenix
from ..units.carrier import Carrier
from ..constants import PYLON_DEFAULT_PORT, pylon_uri


class Gateway:
    """Spawns and manages Zealot agents."""

    def __init__(self, pylon_host: str = "localhost", pylon_port: int = PYLON_DEFAULT_PORT):
        self.pylon_uri = pylon_uri(pylon_host, pylon_port)
        self.unit_types = {
            "zealot": Zealot,
            "tassadar": Tassadar,
            "zeratul": Zeratul,
            "artanis": Artanis,
            "fenix": Fenix,
            "carrier": Carrier,
        }

    def _create_unit(self, unit_type: str, unit_id: str = None):
        """Create unit instance based on type."""
        unit_class = self.unit_types.get(unit_type, Zealot)
        
        # Carrier uses different constructor signature
        if unit_type == "carrier":
            return unit_class(carrier_id=unit_id)
        
        return unit_class(unit_id)

    async def spawn_agent(
        self, task: str, agent_type: str = "zealot", target: str = "nexus"
    ) -> str:
        """Spawn unit for task execution."""

        # Generate unique agent ID
        agent_id = f"{agent_type}-{uuid.uuid4().hex[:8]}"

        # Create unit instance
        unit = self._create_unit(agent_type, agent_id)

        # Connect to Pylon grid
        pylon_uri = f"{self.pylon_uri}/{agent_id}"

        async with websockets.connect(pylon_uri) as websocket:
            print(f"🔹 {agent_id} connected to Pylon grid")

            # Execute task and report result
            result = ""
            try:
                if agent_type == "carrier":
                    # Carrier uses this websocket connection and stays persistent
                    unit.khala_connection = websocket  # Use Gateway's connection
                    print(f"🛸 {agent_id} attuned to Khala network")
                    
                    # Start message handling
                    asyncio.create_task(unit._handle_khala_messages())
                    
                    result = f"Carrier {agent_id} operational - ready for commands"
                    print(f"🛸 {agent_id} ready for conversational commands")
                    
                    # Keep this connection alive - don't return yet
                    # Wait for stop signal or connection close
                    try:
                        # Keep connection alive until explicitly stopped
                        await asyncio.sleep(3600)  # 1 hour timeout
                    except asyncio.CancelledError:
                        print(f"🛸 {agent_id} connection cancelled")
                        return agent_id
                    
                elif hasattr(unit, 'deliberate') and agent_type in ['tassadar', 'zeratul', 'artanis', 'fenix']:
                    # Constitutional agents deliberate
                    result = await unit.deliberate(task)
                else:
                    # Execution agents execute
                    result = await unit.execute(task)
            except Exception as e:
                result = f"Error: {e}"

            # Report completion via Psi
            psi_message = f"§PSI:{target}:{agent_id}:report:{result}"
            await websocket.send(psi_message)
            print(f"⚡ {agent_id} reported to {target}")

        return agent_id


    async def spawn_zealot(self, task: str, target: str = "nexus") -> str:
        """Backward compatibility: spawn zealot agent."""
        return await self.spawn_agent(task, "zealot", target)

    async def spawn_carrier(self, command: str, target: str = "nexus") -> str:
        """Spawn Carrier for human-swarm coordination."""
        return await self.spawn_agent(command, "carrier", target)
