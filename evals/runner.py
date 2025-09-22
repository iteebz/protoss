import asyncio
import shutil
import time
import uuid
import json # Import json for parsing LLM response
from typing import Dict, List, Any

from protoss.core.bus import Bus
from protoss.agents.unit import Unit # Corrected import: BaseAgent -> Unit
from protoss.constitution.identities import get_agent_names
from protoss.lib.paths import Paths  # Import Paths from protoss.lib.paths

from .config import config  # Import the main config object

# Import actual agent classes
from protoss.agents.arbiter import Arbiter
from protoss.agents.archon import Archon
from protoss.agents.conclave import Conclave
from protoss.agents.oracle import Oracle
from protoss.agents.probe import Probe
from protoss.agents.zealot import Zealot

# Import LLM classes directly from cogency.lib.llms
from cogency.lib.llms import Anthropic, Gemini, OpenAI


# Mapping of agent names to their classes
AGENT_CLASSES = {
    "Arbiter": Arbiter,
    "Archon": Archon,
    "Conclave": Conclave,
    "Oracle": Oracle,
    "Probe": Probe,
    "Zealot": Zealot,
}


async def evaluate_protoss_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Runs a single Protoss multi-agent scenario and collects results."""
    test_id = scenario.get("test_id", str(uuid.uuid4()))
    print(f"🧪 Running Protoss Scenario: {test_id}")

    # Setup sandbox
    _prepare_sandbox()

    db_path = None
    bus = None
    agents: List[Unit] = [] # Corrected type hint: BaseAgent -> Unit
    start_time = time.time()

    try:
        # 1. Setup Bus with temporary SQLite storage
        tmpdir = Paths.evals(f"sandbox/{test_id}/bus_db")
        tmpdir.mkdir(parents=True, exist_ok=True)
        db_path = tmpdir / "scenario.db"
        bus = Bus(storage_path=str(db_path), port=0)  # Use random port
        await bus.start()

        # 2. Deploy Agents
        deployed_agent_names = []
        available_agent_names = get_agent_names()

        for agent_type_name in scenario.get("agents_to_deploy", []):
            if (
                agent_type_name in available_agent_names
                and agent_type_name in AGENT_CLASSES
            ):
                print(f"  Deploying {agent_type_name}...")
                AgentClass = AGENT_CLASSES[agent_type_name]
                agent_instance = AgentClass(
                    bus=bus
                )  # Instantiate the agent with the bus
                agents.append(agent_instance)
                await (
                    agent_instance.start()
                )  # Start the agent (e.g., register with bus)
                deployed_agent_names.append(agent_type_name)
            else:
                print(
                    f"  WARNING: Agent type {agent_type_name} not found or not in AGENT_CLASSES."
                )

        # 3. Inject Initial Prompts into the Bus
        initial_prompts = scenario.get("initial_prompts", [])
        for prompt_data in initial_prompts:
            sender = prompt_data.get("sender", "eval_harness")
            channel = prompt_data.get("channel", "general")
            content = prompt_data.get("content", "")
            signals = []  # TODO: Parse signals from content or use explicit signal data
            await bus.transmit(
                channel, sender, event={"content": content}, signals=signals
            )
            print(f"  Injected prompt from {sender} to {channel}: {content[:50]}...")

        # 4. Run Simulation
        simulation_timeout = scenario.get(
            "timeout", config.timeout
        )  # Use main config.timeout
        print(f"  Running simulation for {simulation_timeout} seconds...")
        await asyncio.sleep(simulation_timeout)

        # 5. Collect History
        full_history = await bus.get_history(
            "general"
        )  # Get history for a default channel
        # TODO: Collect history for all relevant channels
        print(f"  Collected {len(full_history)} messages from Bus history.")

        # 6. Judge the result
        judgement = await _judge(full_history, scenario.get("criteria", ""))
        passed = judgement["passed"]
        judge_reason = judgement["judge_reason"]

        return {
            "test_id": test_id,
            "scenario_name": scenario.get("name", "Unnamed Scenario"),
            "duration": round(time.time() - start_time, 2),
            "messages_count": len(full_history),
            "deployed_agents": deployed_agent_names,
            "passed": passed,
            "judge_reason": judge_reason,
            "full_history": [
                msg.to_dict() for msg in full_history
            ],  # Assuming Message has to_dict()
            "criteria": scenario.get("criteria", ""),
        }

    except asyncio.TimeoutError:
        return {"test_id": test_id, "error": "Timeout", "passed": False}
    except Exception as e:
        return {"test_id": test_id, "error": str(e), "passed": False}
    finally:
        if bus:
            await bus.stop()
        for agent in agents:
            await agent.stop()  # Ensure agents are stopped
        if db_path and db_path.exists():
            shutil.rmtree(db_path.parent)  # Clean up the whole sandbox dir


def _prepare_sandbox():
    """Clean sandbox between tests."""
    sandbox = Paths.sandbox()  # Use Paths.sandbox()
    if sandbox.exists():
        shutil.rmtree(sandbox)
    sandbox.mkdir(exist_ok=True)


async def _judge(history: List[Any], criteria: str) -> Dict[str, Any]:
    """Judge Protoss scenario result using an LLM."""
    if not config.judge:
        return {"passed": None, "judge_reason": "Manual review required"}

    # Format the bus history into a readable transcript for the LLM
    transcript = """## Bus Conversation History\n\n"""
    for msg in history:
        # Assuming msg is a Message object with sender, channel, event (with content)
        sender = msg.sender
        content = msg.event.get("content", "")
        timestamp = msg.timestamp.strftime("%H:%M:%S") if msg.timestamp else "N/A"
        transcript += f"[{timestamp}] {sender} on {msg.channel}: {content}\n"
    transcript += "\n" # Add a newline for separation

    # Construct the prompt for the LLM judge
    judge_prompt = f"""You are an impartial judge evaluating a multi-agent conversation on a bus.\nYour task is to determine if the agents successfully met the following criteria:\n\nCriteria: {criteria}\n\nHere is the conversation history:\n{transcript}\n\nDid the agents successfully meet the criteria? Answer PASS or FAIL with brief reason.\n\nFormat: PASS: reason | FAIL: reason"""

    print(f"  Judging scenario with LLM ({config.judge})...")
    try:
        judge_llms = {"openai": OpenAI, "anthropic": Anthropic, "gemini": Gemini}
        if config.judge not in judge_llms:
            return {"passed": False, "judge_reason": f"Unknown judge: {config.judge}"}

        judge_instance = judge_llms[config.judge]()
        messages = [{"role": "user", "content": judge_prompt}]
        response = await judge_instance.generate(messages)

        clean_response = response.strip().upper()
        if clean_response.startswith("PASS"):
            return {"passed": True, "judge_reason": response.strip()}
        if clean_response.startswith("FAIL"):
            return {"passed": False, "judge_reason": response.strip()}
        return {"passed": False, "judge_reason": f"Invalid judge response format: {response}"}

    except Exception as e:
        print(f"  Error during LLM judging: {e}")
        return {"passed": False, "judge_reason": f"LLM judging failed: {e}"}