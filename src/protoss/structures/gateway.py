"""Gateway: Zealot spawning facility.

Spawns Cogency agents, connects to Pylon, executes task, despawns.
"""

import uuid
import websockets
from pathlib import Path
from cogency import Agent
from cogency.tools import FileRead, FileWrite, FileEdit, FileList, SystemShell


class Gateway:
    """Spawns and manages Zealot agents."""

    def __init__(self, pylon_host: str = "localhost", pylon_port: int = 8228):
        self.pylon_uri = f"ws://{pylon_host}:{pylon_port}"
        self.zealot_instructions = self._load_zealot_identity()

    def _load_zealot_identity(self) -> str:
        """Load Zealot identity prompt."""
        prompt_path = Path(__file__).parent / "prompts" / "zealot.md"
        try:
            return prompt_path.read_text().strip()
        except FileNotFoundError:
            return "You are a Zealot agent. Execute tasks with precision and report results."

    def psionic_blades(self):
        """Zealot tool configuration: Files + System execution."""
        return [FileRead(), FileWrite(), FileEdit(), FileList(), SystemShell()]

    async def spawn_zealot(self, task: str, target: str = "nexus") -> str:
        """Spawn Zealot agent for task execution."""

        # Generate unique Zealot ID
        zealot_id = f"zealot-{uuid.uuid4().hex[:8]}"

        # Create Cogency agent with Zealot identity and psionic blades
        agent = Agent(
            instructions=self.zealot_instructions, tools=self.psionic_blades()
        )

        # Connect to Pylon grid
        pylon_uri = f"{self.pylon_uri}/{zealot_id}"

        async with websockets.connect(pylon_uri) as websocket:
            print(f"🔹 {zealot_id} connected to Pylon grid")

            # Execute task via Cogency
            print(f"🔹 {zealot_id} executing task: {task}")
            result = ""
            try:
                async for event in agent.stream(task, conversation_id=zealot_id):
                    if event.get("type") == "respond":
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
