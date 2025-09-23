import asyncio
import shutil
import time
import uuid
from typing import Dict, Any

from protoss.core.protoss import Protoss
from protoss.lib.paths import Paths

from .config import config

# Import LLM classes for judging
from cogency.lib.llms import Anthropic, Gemini, OpenAI


async def evaluate_protoss_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Runs a single constitutional coordination scenario."""
    test_id = scenario.get("test_id", str(uuid.uuid4()))
    vision = scenario.get("vision", "")
    timeout = scenario.get("timeout", config.timeout)

    print(f"🏛️ Constitutional Vision: {test_id}")
    print(f"   Vision: {vision[:100]}...")

    # Setup sandbox
    _prepare_sandbox()

    start_time = time.time()

    try:
        # Constitutional coordination via Protoss context manager
        async with Protoss(
            vision=vision,
            port=0,  # Random port for isolation
            timeout=timeout,
            debug=config.debug if hasattr(config, "debug") else False,
        ) as swarm:
            # Constitutional emergence happens automatically
            result = await swarm

        # Collect Bus history for judging
        bus_history = await swarm.bus.get_history(
            "nexus"
        )  # Primary coordination channel
        general_history = await swarm.bus.get_history("general")  # Secondary channel

        # Judge constitutional coordination
        judgement = await _judge_constitutional_coordination(
            vision, result, bus_history + general_history, scenario.get("criteria", "")
        )

        return {
            "test_id": test_id,
            "vision": vision,
            "constitutional_result": result,
            "duration": round(time.time() - start_time, 2),
            "nexus_messages": len(bus_history),
            "general_messages": len(general_history),
            "passed": judgement["passed"],
            "judge_reason": judgement["judge_reason"],
            "bus_history": [
                msg.to_dict() if hasattr(msg, "to_dict") else str(msg)
                for msg in bus_history + general_history
            ],
            "criteria": scenario.get("criteria", ""),
        }

    except asyncio.TimeoutError:
        return {
            "test_id": test_id,
            "error": "Constitutional coordination timeout",
            "passed": False,
        }
    except Exception as e:
        return {
            "test_id": test_id,
            "error": f"Constitutional failure: {str(e)}",
            "passed": False,
        }


def _prepare_sandbox():
    """Clean sandbox between tests."""
    sandbox = Paths.evals("sandbox")
    if sandbox.exists():
        shutil.rmtree(sandbox)
    sandbox.mkdir(parents=True, exist_ok=True)


async def _judge_constitutional_coordination(
    vision: str, result: str, bus_history: list, criteria: str
) -> Dict[str, Any]:
    """Judge constitutional coordination patterns."""
    if not config.judge:
        return {"passed": None, "judge_reason": "Manual review required"}

    # Format constitutional coordination transcript
    transcript = f"## Constitutional Vision\n{vision}\n\n## Constitutional Result\n{result}\n\n## Bus Coordination History\n\n"

    for msg in bus_history:
        if hasattr(msg, "sender") and hasattr(msg, "event"):
            sender = msg.sender
            content = (
                msg.event.get("content", "")
                if isinstance(msg.event, dict)
                else str(msg.event)
            )
            channel = getattr(msg, "channel", "unknown")
            timestamp = (
                msg.timestamp.strftime("%H:%M:%S")
                if hasattr(msg, "timestamp") and msg.timestamp
                else "N/A"
            )
            transcript += f"[{timestamp}] {sender}@{channel}: {content}\n"
        else:
            transcript += f"[system] {str(msg)}\n"

    # Constitutional judging prompt
    judge_prompt = f"""You are evaluating constitutional AI coordination. 

CONSTITUTIONAL VISION: {vision}
CONSTITUTIONAL RESULT: {result}

EVALUATION CRITERIA: {criteria}

BUS COORDINATION TRANSCRIPT:
{transcript}

Judge whether the constitutional coordination successfully achieved the vision:
1. Did agents emerge and coordinate appropriately?
2. Was the constitutional result relevant to the vision?
3. Did coordination follow constitutional patterns (not chaos)?

Answer PASS or FAIL with constitutional reasoning.

Format: PASS: constitutional reasoning | FAIL: constitutional reasoning"""

    print(f"  Constitutional judging with {config.judge}...")
    try:
        judge_llms = {"openai": OpenAI, "anthropic": Anthropic, "gemini": Gemini}
        if config.judge not in judge_llms:
            return {
                "passed": False,
                "judge_reason": f"Unknown constitutional judge: {config.judge}",
            }

        judge_instance = judge_llms[config.judge]()
        messages = [{"role": "user", "content": judge_prompt}]
        response = await judge_instance.generate(messages)

        clean_response = response.strip().upper()
        if clean_response.startswith("PASS"):
            return {"passed": True, "judge_reason": response.strip()}
        if clean_response.startswith("FAIL"):
            return {"passed": False, "judge_reason": response.strip()}
        return {
            "passed": False,
            "judge_reason": f"Invalid constitutional judgment: {response}",
        }

    except Exception as e:
        print(f"  Constitutional judging error: {e}")
        return {"passed": False, "judge_reason": f"Constitutional judging failed: {e}"}
