"""Pylon: Infrastructure that enables Protoss coordination.

Power grid and WebSocket infrastructure. Enables the Khala to operate.
All coordination logic handled by Khala - Pylon provides pure infrastructure.
"""

import asyncio
from typing import Dict
import websockets
from ..khala import khala, Psi
from ..constants import PYLON_DEFAULT_PORT


class Pylon:
    """Infrastructure that powers the coordination grid. Enables the Khala to operate."""

    def __init__(self, port: int = PYLON_DEFAULT_PORT):
        self.port = port
        self.agents: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.khala = khala  # The psychic network we power

    async def start(self):
        """Power up the grid - start WebSocket infrastructure."""
        self.server = await websockets.serve(
            self._handle_connection, "localhost", self.port
        )
        print(f"🔹 Pylon powered up on ws://localhost:{self.port}")

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
                    # All messages go directly to Khala
                    await self.khala.transmit(psi=message)
        finally:
            self.agents.pop(agent_id, None)
            # Remove agent from all Khala pathways
            self.khala.sever(agent_id)


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

