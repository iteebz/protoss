#!/usr/bin/env python3
"""Trial by Fire: Testing conversational emergence with team coordination.

Agents coordinate through conversation to build working software.
"""

import asyncio
import logging
import time
import uuid
from src.protoss.core.protoss import Protoss

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)


async def trial_by_fire():
    """Team coordination challenge."""

    run_id = uuid.uuid4().hex[:8]
    channel = f"flask-api-{run_id}"
    base_dir = f"./trials/{run_id}"

    protoss = Protoss(channel=channel, base_dir=base_dir)

    print("🔥 TRIAL BY FIRE: Team Coordination")
    print(f"Channel: #{channel}")
    print(f"Workspace: {base_dir}")
    print()

    # Minimal coordination prompt - let emergence happen
    await protoss.send_human_message("""
🔥 BUILD WORKING SOFTWARE

Team objective: Complete Flask REST API supporting /users, /posts, /comments

Coordinate through conversation. Claim work. Execute. Signal !despawn when done.
""")

    print("🔥 Spawning team with staggered coordination...")

    # Staggered spawning for better coordination
    await protoss.spawn_agent("zealot")
    await asyncio.sleep(2)
    await protoss.spawn_agent("sentinel")
    await asyncio.sleep(2)
    await protoss.spawn_agent("harbinger")

    print("🔥 Team assembled. Monitoring coordination...")
    print()

    # Monitor coordination with natural exit detection
    timeout = 120
    check_interval = 10
    start_time = time.time()
    last_message_count = 0
    silence_threshold = 30  # Exit if no new messages for 30 seconds

    last_activity_time = start_time

    while time.time() - start_time < timeout:
        await asyncio.sleep(check_interval)

        conversation = await protoss.get_conversation(channel)
        current_message_count = len(conversation) if conversation else 0

        # Exit if no new messages for silence_threshold
        if current_message_count > last_message_count:
            last_message_count = current_message_count
            last_activity_time = time.time()
        elif time.time() - last_activity_time > silence_threshold:
            print(f"🔥 Natural completion detected (quiet for {silence_threshold}s)")
            break

    # Show results
    conversation = await protoss.get_conversation(channel)

    print("\n🔥 COORDINATION REPORT")
    print("═════════════════════════════════════════════════════════")
    print(f"Messages: {len(conversation)}")
    print("Recent coordination:")
    print()

    for msg in conversation[-6:]:
        sender = msg["sender"].upper() if msg["sender"] != "human" else "HUMAN"
        content = (
            msg["content"][:160] + "..."
            if len(msg["content"]) > 160
            else msg["content"]
        )
        print(f"{sender}: {content}")
        print()

    # Check coordination patterns
    claims = [
        msg
        for msg in conversation
        if "i'll handle" in msg["content"].lower()
        or "i'll take" in msg["content"].lower()
    ]
    reports = [
        msg
        for msg in conversation
        if "completed" in msg["content"].lower() or "finished" in msg["content"].lower()
    ]
    human_asks = [
        msg
        for msg in conversation
        if any(
            phrase in msg["content"].lower()
            for phrase in ["please try", "please run", "please navigate"]
        )
    ]
    team_help = [
        msg
        for msg in conversation
        if any(
            phrase in msg["content"].lower()
            for phrase in ["any ideas", "getting error", "teammates"]
        )
    ]

    print(f"📋 Task claims: {len(claims)}")
    print(f"✅ Progress reports: {len(reports)}")
    print(f"❌ Human instruction attempts: {len(human_asks)}")
    print(f"🤝 Team collaboration: {len(team_help)}")
    print(f"🗂️  Workspace: {base_dir}")

    # Simplified success metrics
    if len(claims) >= 3 and len(conversation) >= 15:
        print("🔥 SUCCESS: Autonomous coordination achieved")
    elif len(claims) > 0:
        print("🔥 PROGRESS: Coordination emerging")
    else:
        print("🔥 LEARNING: Need more emergence")


if __name__ == "__main__":
    print()
    print("🔥🔥🔥 PROTOSS TRIAL BY FIRE 🔥🔥🔥")
    print("Testing team coordination through conversation")
    print()

    asyncio.run(trial_by_fire())
