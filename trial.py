#!/usr/bin/env python3
"""Pure emergence trial: Can agents coordinate without scaffolding?

Hypothesis: LLM agents can discover coordination protocols through
conversation and filesystem observation alone.

Design: 3 agents, shared workspace, shared conversation, minimal prompt.
Success: Working Flask API with /users, /posts, /comments in <100 messages.
"""

import asyncio
import json
import logging
import shutil
import time
import uuid
from pathlib import Path

from src.protoss.core.protoss import Protoss

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)


async def run_trial():
    """Run single emergence trial."""
    run_id = uuid.uuid4().hex[:8]
    channel = f"trial-{run_id}"
    base_dir = f"./trials/{run_id}"

    protoss = Protoss(channel=channel, base_dir=base_dir)

    # Snapshot coordination.py and constitutions for reproducibility
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy(
        "src/protoss/constitution/coordination.py", f"{base_dir}/coordination.py"
    )
    for agent in ["zealot", "sentinel", "harbinger"]:
        src = f"src/protoss/constitution/{agent}.py"
        if Path(src).exists():
            shutil.copy(src, f"{base_dir}/{agent}.py")

    print(f"🧪 TRIAL {run_id}")
    print(f"   Channel: #{channel}")
    print(f"   Workspace: {base_dir}")
    print()

    # Task specification (explicit parallel pressure)
    await protoss.send_human_message(
        "Build calculator with add, subtract, multiply, divide functions. "
        "Work in parallel where possible. Integrate when done."
    )

    # Spawn agents simultaneously (no staggering)
    await asyncio.gather(
        protoss.spawn_agent("zealot"),
        protoss.spawn_agent("sentinel"),
        protoss.spawn_agent("harbinger"),
    )

    # Hard limits: 50 messages OR 5 minutes
    max_messages = 50
    timeout = 300
    check_interval = 5
    start_time = time.time()

    while time.time() - start_time < timeout:
        await asyncio.sleep(check_interval)
        conversation = await protoss.get_conversation(channel)

        if len(conversation) >= max_messages:
            print(f"⏱️  Message limit reached ({max_messages})")
            break

    # Export conversation log
    conversation = await protoss.get_conversation(channel)
    chat_log = f"{base_dir}/chat.json"
    with open(chat_log, "w") as f:
        json.dump(conversation, f, indent=2)

    # Export readable markdown
    md_log = f"{base_dir}/chat.md"
    with open(md_log, "w") as f:
        f.write(f"# Trial {run_id}\n\n")
        f.write(f"**Messages:** {len(conversation)}\n")
        f.write(f"**Duration:** {time.time() - start_time:.1f}s\n\n")
        f.write("---\n\n")
        for msg in conversation:
            sender = msg["sender"].upper()
            content = msg["content"]
            f.write(f"### {sender}\n\n{content}\n\n")

    # Export errors for debugging
    all_errors = []
    for agent in protoss.agents:
        all_errors.extend(agent.errors)

    if all_errors:
        errors_log = f"{base_dir}/errors.md"
        with open(errors_log, "w") as f:
            f.write(f"# Tool Errors - Trial {run_id}\n\n")
            f.write(f"**Total Errors:** {len(all_errors)}\n\n")
            f.write("---\n\n")
            for err in all_errors:
                f.write(f"## {err['agent']} → {err['tool']}\n\n")
                f.write(f"**Call:** `{json.dumps(err['call'])}`\n\n")
                f.write(f"**Outcome:** {err['outcome']}\n\n")
                f.write("---\n\n")

    # Analyze workspace
    sandbox = Path(f"{base_dir}/sandbox")
    files = list(sandbox.glob("**/*.py")) if sandbox.exists() else []

    # Check for success
    has_calculator = any("calculator" in f.name.lower() or "calc" in f.name.lower() for f in files)
    has_operations = any(op in f.read_text() for op in ["add", "subtract", "multiply", "divide"] for f in files if f.suffix == ".py")
    success = has_calculator and has_operations and len(files) >= 1

    # Report
    print("\n📊 RESULTS")
    print(f"   Messages: {len(conversation)}")
    print(f"   Files: {len(files)}")
    print(f"   Success: {'✅' if success else '❌'}")
    print(f"   Logs: {md_log}")
    print()

    return {
        "run_id": run_id,
        "messages": len(conversation),
        "files": len(files),
        "success": success,
        "duration": time.time() - start_time,
    }


async def run_batch(count: int):
    """Run batch of trials."""
    print("🧪 EMERGENCE EXPERIMENT")
    print(f"   Trials: {count}")
    print("   Limit: 50 messages OR 5 minutes")
    print("   Model: gpt-4.1-mini")
    print()

    results = []
    for i in range(count):
        print(f"▶️  Trial {i+1}/{count}")
        result = await run_trial()
        results.append(result)

        # Brief pause between trials
        if i < count - 1:
            await asyncio.sleep(2)

    # Summary
    successes = sum(1 for r in results if r["success"])
    avg_messages = sum(r["messages"] for r in results) / len(results)
    avg_files = sum(r["files"] for r in results) / len(results)

    print("\n" + "=" * 60)
    print("📈 BATCH SUMMARY")
    print("=" * 60)
    print(f"Success rate: {successes}/{count} ({successes/count*100:.1f}%)")
    print(f"Avg messages: {avg_messages:.1f}")
    print(f"Avg files: {avg_files:.1f}")
    print()

    # Save summary
    summary_path = f"./trials/batch_{int(time.time())}.json"
    with open(summary_path, "w") as f:
        json.dump(
            {
                "results": results,
                "summary": {
                    "success_rate": successes / count,
                    "avg_messages": avg_messages,
                    "avg_files": avg_files,
                },
            },
            f,
            indent=2,
        )

    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    asyncio.run(run_batch(count))
