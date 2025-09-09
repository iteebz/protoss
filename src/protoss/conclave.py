"""Conclave: The sacred four provide AI oversight through constitutional debate."""

import asyncio
import uuid
import websockets
from pathlib import Path
from cogency import Agent
from .constants import PYLON_DEFAULT_PORT, pylon_uri


class Conclave:
    """The sacred four - Tassadar, Zeratul, Artanis, Fenix - provide AI oversight."""

    def __init__(self, pylon_host: str = "localhost", pylon_port: int = PYLON_DEFAULT_PORT):
        self.pylon_uri = pylon_uri(pylon_host, pylon_port)
        self.prompts_dir = Path(__file__).parent / "prompts"

    async def convene(self, task: str) -> str:
        """Convene the sacred four for constitutional deliberation."""
        conclave_id = f"conclave-{uuid.uuid4().hex[:8]}"
        the_sacred_four = ["tassadar", "zeratul", "artanis", "fenix"]

        print(f"🔮 Convening Sacred Four on pathway {conclave_id}")
        print(f"📋 Question: {task}")

        # Spawn conclave participants concurrently
        tasks = [
            self._spawn_participant(agent_type, task, conclave_id)
            for agent_type in the_sacred_four
        ]

        await asyncio.gather(*tasks)
        return conclave_id

    def _load_prompt(self, agent_type: str) -> str:
        """Load constitutional prompt for agent type."""
        prompt_path = self.prompts_dir / f"{agent_type}.md"
        try:
            return prompt_path.read_text().strip()
        except FileNotFoundError:
            return f"You are a {agent_type.title()} agent. Execute tasks with precision and report results."

    def _psionic_blades(self, agent_type: str = "zealot"):
        """Tool configuration - conclave agents get no tools for pure constitutional reasoning."""
        return []  # Pure constitutional reasoning, no external tools

    async def _spawn_participant(self, agent_type: str, task: str, conclave_id: str):
        """Spawn individual conclave participant."""
        # Generate unique agent ID
        agent_id = f"{agent_type}-{uuid.uuid4().hex[:8]}"

        # Load constitutional identity
        instructions = self._load_prompt(agent_type)
        tools = self._psionic_blades(agent_type)
        agent = Agent(instructions=instructions, tools=tools)

        # Get initial position on the question
        position = await self._position(agent, agent_id, task)
        print(f"💭 {agent_id}: {position[:80]}...")

        # Connect to conclave pathway and participate
        pylon_uri = f"{self.pylon_uri}/{agent_id}"
        
        async with websockets.connect(pylon_uri) as websocket:
            print(f"🔹 {agent_id} joined conclave pathway")
            await self._participate(agent, agent_id, position, conclave_id, websocket)

    async def _position(self, agent, agent_id: str, task: str) -> str:
        """Get agent's independent position on task."""
        # Extract the core question from the nested task string
        core_task = "No question provided"
        
        # The task comes in nested format: "TASK: QUESTION FOR DELIBERATION: actual_question"
        if "QUESTION FOR DELIBERATION: " in task:
            # Find the actual question after the nested prefix
            start = task.find("QUESTION FOR DELIBERATION: ") + len("QUESTION FOR DELIBERATION: ")
            end = task.find("\n", start)
            if end == -1:
                end = len(task)
            core_task = task[start:end].strip()
        elif "TASK: " in task:
            # Handle direct TASK format
            start = task.find("TASK: ") + len("TASK: ")
            end = task.find("\n", start)
            if end == -1:
                end = len(task)
            core_task = task[start:end].strip()
        else:
            core_task = task.strip()
        
        # Debug output
        print(f"🔍 {agent_id} extracted question: '{core_task}'")

        prompt = f"""
You must form your constitutional position on this question:

{core_task}

Based on your identity and values, provide your definitive stance with reasoning. This position will be defended in the Conclave.
"""

        try:
            async for event in agent.stream(prompt, conversation_id=f"{agent_id}-pos"):
                if event.get("type") == "respond":
                    position = event.get("content", "").strip()
                    return position.split("\n\n")[0] if position else "No position"
        except Exception as e:
            return f"Error: {e}"

        return "No position"

    async def _participate(
        self, agent, agent_id: str, position: str, conclave_id: str, websocket
    ):
        """Agent participates in pure reactive conclave discussion."""

        # Present initial position
        msg = f"§PSI:{conclave_id}:{agent_id}:position:{position}"
        await websocket.send(msg)
        print(f"💭 {agent_id} presented position")

        # Set up reactive discussion
        discussion_context = f"""
You are participating in conclave discussion on pathway {conclave_id}.
Your constitutional position: {position}

You will receive messages from other agents. Respond naturally when:
- You disagree with another position
- Someone addresses you directly
- You want to clarify or defend your stance
- You have new insights based on the discussion

Respond through Psi messages: §PSI:{conclave_id}:{agent_id}:discuss:your_response
When you're done participating, send: §PSI:{conclave_id}:{agent_id}:departing:final_thoughts
"""

        # Agent listens and responds naturally via WebSocket stream
        try:
            # The agent should receive all pathway messages via Khala
            # and decide when/how to respond based on constitutional identity
            async for message in websocket:
                # Let agent process incoming message and decide response
                prompt = f"{discussion_context}\n\nIncoming: {message}\n\nRespond if appropriate:"
                
                async for event in agent.stream(prompt, conversation_id=f"{agent_id}-conclave"):
                    if event.get("type") == "respond":
                        response = event.get("content", "").strip()
                        if response and not response.lower().startswith("no response"):
                            await websocket.send(response)
                            print(f"⚡ {agent_id}: {response[:50]}...")
                        break

        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 {agent_id} connection closed")
        except Exception as e:
            print(f"❌ {agent_id} error: {e}")
            # Graceful departure
            farewell = f"§PSI:{conclave_id}:{agent_id}:departing:Connection error - departing conclave"
            try:
                await websocket.send(farewell)
            except Exception:
                pass


def load_persona(name: str) -> str:
    """Load persona prompt from file."""
    prompt_path = Path(__file__).parent / "prompts" / f"{name}.md"
    if prompt_path.exists():
        return prompt_path.read_text()
    return f"# {name.upper()} - Persona not found"


def simulate_response(persona_name: str, question: str) -> str:
    """Simulate persona response based on archetype."""
    archetypes = {
        "tassadar": "Strategic vision balanced with shipping reality",
        "zeratul": "Deep investigation, questioning assumptions",
        "artanis": "Collaborative synthesis, finding unity",
        "fenix": "Direct execution, cutting through complexity",
    }

    archetype = archetypes.get(persona_name, "Unknown archetype")
    return f"[{archetype}] {question}"


async def full_debate(question: str):
    """Run actual Conclave debate with real AI agents."""
    from .structures.pylon import Pylon
    from .structures.gateway import Gateway

    # Start infrastructure on main grid
    pylon = Pylon()  # Uses default port 8888
    await pylon.start()
    print("🔹 Pylon grid powered for sacred debate")

    gateway = Gateway()  # Uses default port 8888
    conclave = Conclave()  # Uses default port 8888

    # Format the question as a proper task
    task = f"""
QUESTION FOR DELIBERATION: {question}

Sacred Four: Deliberate on this matter through your constitutional perspectives.
Each member should present their position based on their unique archetype and values.
"""

    print(f"🔮 Convening the sacred four for deliberation on: {question}")
    conclave_id = await conclave.convene(task)
    print(f"⚡ Conclave pathway: {conclave_id}")

    # Let the debate run for 30 seconds
    print("🧠 The sacred four deliberate through the Khala...")
    await asyncio.sleep(30)

    # Get the full dialogue
    print("\n" + "=" * 60)
    print("🔮 CONCLAVE DIALOGUE")
    print("=" * 60)

    pathway_details = pylon.get_pathway(conclave_id)
    if pathway_details:
        print(f'📊 Total thoughts exchanged: {pathway_details["memory_count"]}')
        print("\n💭 Sacred dialogue:\n")

        for i, memory in enumerate(pathway_details.get("recent_memories", []), 1):
            if memory.startswith("§PSI:"):
                parts = memory.split(":", 4)
                if len(parts) >= 5:
                    speaker = parts[2].split("-")[0]
                    content = parts[4]
                    print(f"{i}. 【{speaker.upper()}】: {content}\n")

        print("=" * 60)
        print("🔥 Sacred debate concluded. The Khala has spoken.")
    else:
        print("❌ No pathway found - debate may not have started")

    await pylon.stop()
    print("⚡ EN TARO ADUN!")


def deliberate(question: str):
    """CLI entry point for Conclave deliberation."""
    print("🔮 INITIALIZING FULL CONCLAVE DEBATE...")
    print("⚡ (This will spawn real AI agents - may take 30+ seconds)")
    print()

    try:
        asyncio.run(full_debate(question))
    except KeyboardInterrupt:
        print("\n⚡ Conclave interrupted. En taro Adun.")
    except Exception as e:
        print(f"\n❌ Conclave error: {e}")
        print("🔥 The sacred four could not convene.")
