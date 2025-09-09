"""Pylon: Infrastructure that enables Protoss coordination.

Power grid and WebSocket infrastructure. Enables the Khala to operate.
All coordination logic handled by Khala - Pylon provides pure infrastructure.
"""

import asyncio
from typing import Dict
import websockets
from ..khala import Khala, Psi
from ..constants import PYLON_DEFAULT_PORT


class Pylon:
    """Infrastructure that powers the coordination grid. Enables the Khala to operate."""

    def __init__(self, port: int = PYLON_DEFAULT_PORT):
        self.port = port
        self.agents: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.khala = Khala()  # The psychic network we power

    async def start(self):
        """Power up the grid - start WebSocket infrastructure."""
        self.server = await websockets.serve(
            self._handle_connection, "localhost", self.port
        )

    async def stop(self):
        """Power down the grid."""
        if hasattr(self, "server"):
            self.server.close()
            await self.server.wait_closed()

    async def _attune_memories(self, agent_id: str, websocket):
        """Send recent memories from agent's Khala pathways."""
        # Send recent memories from pathways the agent was attuned to
        for pathway_name, minds in self.khala.subscribers.items():
            if agent_id in minds:
                memories = self.khala.attune(
                    agent_id, pathway_name
                )  # Re-attune and get memories
                for message in memories:
                    try:
                        await websocket.send(message.serialize())
                    except websockets.exceptions.ConnectionClosed:
                        return

    async def _handle_connection(self, websocket):
        """Handle agent connection to grid."""
        agent_id = websocket.request.path.strip("/")
        self.agents[agent_id] = websocket

        # Send memories from pathways agent was previously attuned to
        await self._attune_memories(agent_id, websocket)
        print(f"🔹 {agent_id} connected to Pylon grid")

        try:
            async for raw_message in websocket:
                message = Psi.parse(raw_message)
                if message:
                    # Forward to appropriate handler
                    if message.type == "inspect":
                        await self._handle_inspection(message)
                    else:
                        # All coordination goes directly to Khala
                        await self.khala.transmit(message, self.agents)
        finally:
            self.agents.pop(agent_id, None)
            # Remove agent from all Khala pathways
            self.khala.sever(agent_id)

    async def _handle_inspection(self, message: Psi):
        """Handle inspection commands from CLI."""
        command = message.content
        agent_socket = self.agents.get(message.source)
        
        if not agent_socket:
            return
            
        try:
            import json
            
            if command == "status":
                result = self.get_status()
            elif command == "pathways":
                result = {"pathways": self.get_pathways()}
            elif command == "minds":
                result = {"minds": self.get_minds()}
            elif command.startswith("pathway:"):
                pathway_name = command.split(":", 1)[1]
                pathway_details = self.get_pathway(pathway_name)
                result = {"pathway": pathway_details}
            elif command.startswith("carrier_command:"):
                # Route command to active Carrier
                human_command = command.split(":", 1)[1]
                result = await self._route_to_carrier(human_command)
            elif command == "carrier_status":
                result = await self._get_carrier_status()
            elif command == "carrier_stop":
                result = await self._stop_carrier()
            else:
                result = {"error": f"Unknown command: {command}"}
            
            # Send result back to inspector
            response = f"§PSI:inspector:{message.source}:result:{json.dumps(result)}"
            await agent_socket.send(response)
            
        except Exception as e:
            error_response = f"§PSI:inspector:{message.source}:result:{json.dumps({'error': str(e)})}"
            await agent_socket.send(error_response)

    # CLI INSPECTION METHODS - DELEGATE TO COMPONENTS

    def get_status(self) -> dict:
        """Get Pylon system status."""
        khala_status = self.khala.get_status()
        return {"active_agents": len(self.agents), **khala_status}

    def get_pathways(self):
        """Get all Khala pathways with stats."""
        return self.khala.get_pathways()

    def get_pathway(self, name: str):
        """Get pathway details."""
        return self.khala.get_pathway(name)

    def get_minds(self):
        """Get all minds with pathways."""
        return self.khala.get_minds(self.agents)

    # CARRIER COORDINATION METHODS

    def _find_active_carrier(self) -> str:
        """Find active Carrier agent ID."""
        for agent_id in self.agents:
            if agent_id.startswith("carrier-"):
                return agent_id
        return None

    async def _route_to_carrier(self, human_command: str) -> dict:
        """Route human command to active Carrier."""
        carrier_id = self._find_active_carrier()
        
        if not carrier_id:
            return {"error": "No active Carrier. Spawn with: protoss carrier spawn"}
        
        try:
            # Send command to Carrier via Khala
            command_psi = Psi(
                target=carrier_id,
                source="cli-interface",
                type="human_command",
                content=human_command
            )
            
            carrier_socket = self.agents.get(carrier_id)
            if carrier_socket:
                await carrier_socket.send(command_psi.serialize())
                
                # For now, return immediate acknowledgment
                # In full implementation, would await Carrier response
                return {
                    "response": f"Command routed to {carrier_id}. Processing..."
                }
            else:
                return {"error": f"Carrier {carrier_id} socket not found"}
                
        except Exception as e:
            return {"error": f"Carrier communication failed: {e}"}

    async def _get_carrier_status(self) -> dict:
        """Get Carrier coordination status."""
        carrier_id = self._find_active_carrier()
        
        if not carrier_id:
            return {"error": "No active Carrier"}
        
        # For MVP, return basic status
        # In full implementation, would query Carrier directly
        return {
            "status": {
                "carrier_id": carrier_id,
                "active_interceptors": 0,  # Would query Carrier
                "context_buffer_size": 0,
                "coordination_capacity": "optimal",
                "health": "operational"
            }
        }

    async def _stop_carrier(self) -> dict:
        """Stop active Carrier."""
        carrier_id = self._find_active_carrier()
        
        if not carrier_id:
            return {"error": "No active Carrier to stop"}
        
        try:
            # Send stop command to Carrier
            stop_psi = Psi(
                target=carrier_id,
                source="cli-interface", 
                type="stop",
                content="Despawn request from CLI"
            )
            
            carrier_socket = self.agents.get(carrier_id)
            if carrier_socket:
                await carrier_socket.send(stop_psi.serialize())
                
                # Remove from active agents
                self.agents.pop(carrier_id, None)
                self.khala.sever(carrier_id)
                
                return {"message": f"Carrier {carrier_id} despawned"}
            else:
                return {"error": f"Carrier {carrier_id} socket not found"}
                
        except Exception as e:
            return {"error": f"Carrier stop failed: {e}"}
