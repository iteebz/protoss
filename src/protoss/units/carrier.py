"""Carrier: Human-swarm emissary for coordination scaling.

Mobile bridge between Nexus (human command center) and Khala (agent coordination).
The Carrier is the solution to the "1 human : 100 agent" coordination bottleneck.
"""

import uuid
import asyncio
import websockets
from typing import Optional, Dict, Any
from ..khala import Psi
from ..constants import pylon_uri, PYLON_DEFAULT_PORT


class Carrier:
    """Human-swarm emissary. Clean interface between human commands and agent coordination."""

    def __init__(
        self, 
        carrier_id: str = None,
        pylon_host: str = "localhost",
        pylon_port: int = PYLON_DEFAULT_PORT
    ):
        self.id = carrier_id or f"carrier-{uuid.uuid4().hex[:8]}"
        self.pylon_uri = pylon_uri(pylon_host, pylon_port)
        self.khala_connection: Optional[websockets.WebSocketClientProtocol] = None

    async def connect_to_khala(self):
        """Connect to Khala network for coordination."""
        if self.khala_connection:
            return
            
        try:
            connection_uri = f"{self.pylon_uri}/{self.id}"
            self.khala_connection = await websockets.connect(connection_uri)
            print(f"🛸 {self.id} attuned to Khala network")
            
            asyncio.create_task(self._handle_khala_messages())
            
        except Exception as e:
            print(f"❌ Khala connection failed: {e}")

    async def _handle_khala_messages(self):
        """Handle incoming messages from Khala network."""
        if not self.khala_connection:
            return
            
        try:
            async for raw_message in self.khala_connection:
                psi = Psi.parse(raw_message)
                if psi and psi.type == "command":
                    response = f"Processing: {psi.content}"
                    
                    response_psi = Psi(
                        target=psi.source,
                        source=self.id,
                        type="response", 
                        content=response
                    )
                    
                    await self.khala_connection.send(response_psi.serialize())
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"🛸 {self.id} Khala connection closed")
            self.khala_connection = None

    async def despawn(self):
        """Gracefully despawn Carrier."""
        if self.khala_connection:
            await self.khala_connection.close()
            self.khala_connection = None
        print(f"⚡ {self.id} - En Taro Adun!")