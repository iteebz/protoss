#!/usr/bin/env python3
"""Debug agent coordination."""

import asyncio
import logging
import uuid
from src.protoss.swarm import Swarm

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def debug_agents():
    """Debug single agent response."""
    
    run_id = uuid.uuid4().hex[:8]
    channel = f"debug-{run_id}"
    base_dir = f"./debug-run-{run_id}"
    
    swarm = Swarm(channel=channel, base_dir=base_dir)
    
    print(f"Debug in #{channel}")
    
    # Simple task
    await swarm.send_human_message("Build a simple HTML hello world page. Just say what you'll do and do it.")
    
    # Spawn just one agent
    await swarm.spawn_agent("zealot")
    
    # Give it time
    await asyncio.sleep(15)
    
    # Check conversation
    conversation = swarm.get_conversation(channel)
    print(f"\n=== CONVERSATION ({len(conversation)} messages) ===")
    for msg in conversation:
        sender = msg['sender'].upper()
        print(f"{sender}: {msg['content'][:100]}")
    
    print(f"\nTest run: {base_dir}")

if __name__ == "__main__":
    asyncio.run(debug_agents())