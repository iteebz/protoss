"""Gateway: Zealot spawning facility.

Spawns Cogency agents, connects to Pylon, executes task, despawns.
"""

import uuid
import websockets
from cogency import Agent


class Gateway:
    """Spawns and manages Zealot agents."""

    def __init__(self, pylon_host: str = "localhost", pylon_port: int = 8228):
        self.pylon_uri = f"ws://{pylon_host}:{pylon_port}"

    async def spawn_zealot(self, task: str, target: str = "nexus") -> str:
        """Spawn Zealot agent for task execution."""

        # Generate unique Zealot ID
        zealot_id = f"zealot-{uuid.uuid4().hex[:8]}"

        # Create Cogency agent
        agent = Agent()

        # Connect to Pylon grid
        pylon_uri = f"{self.pylon_uri}/{zealot_id}"

        async with websockets.connect(pylon_uri) as websocket:
            print(f"🔹 {zealot_id} connected to Pylon grid")

            # Execute task via Cogency
            print(f"🔹 {zealot_id} executing task: {task}")
            result = ""
            try:
                async for event in agent.stream(task, conversation_id=zealot_id):
                    if event.get("type") and event["type"].value == "respond":
                        result = event.get("content", "")
                        print(f"🔹 {zealot_id} received response: {result}")
                        break
            except Exception as e:
                result = f"Error: {e}"

            # Report completion via Psi
            psi_message = f"§PSI:{target}:{zealot_id}:report:{result}"
            await websocket.send(psi_message)
            print(f"🔹 {zealot_id} task complete, reported to {target}")

            # Zealot despawns (connection closes)

        return zealot_id
