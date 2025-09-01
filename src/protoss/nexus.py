"""Nexus: Central coordination hub for Protoss agent swarms."""

import asyncio
import websockets
from .gateway import Gateway
from .pylon import Pylon


class Nexus:
    """Central coordination hub. Human interface to Protoss swarm."""

    def __init__(self, pylon_port: int = 8228):
        self.pylon_port = pylon_port
        self.gateway = Gateway(pylon_port=pylon_port)
        self.pylon = None

    async def start(self):
        """Initialize Nexus with Pylon grid."""
        self.pylon = Pylon(port=self.pylon_port)
        await self.pylon.start()
        print("🔹 Nexus online - Pylon grid powered")

    async def execute_task(self, task: str) -> str:
        """Execute task via Gateway → Zealot → Pylon → response."""

        # Connect to Pylon as Nexus
        nexus_uri = f"ws://localhost:{self.pylon_port}/nexus"

        async with websockets.connect(nexus_uri) as websocket:
            print("🔹 Nexus connected to grid")

            # Spawn Zealot via Gateway
            asyncio.create_task(self.gateway.spawn_zealot(task, target="nexus"))

            # Wait for Zealot report
            result_message = await websocket.recv()
            print(f"🔹 Nexus received: {result_message}")

            # Extract result from Psi message
            # §PSI:nexus:zealot-id:report:actual-result
            if result_message.startswith("§PSI:"):
                result = result_message.split(":", 4)[-1]
                return result

            return "No result received"
