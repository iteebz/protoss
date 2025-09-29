#!/usr/bin/env python3
"""Test agents debating and responding to each other."""

import asyncio
import logging
import uuid
from src.protoss.swarm import Swarm

logging.basicConfig(level=logging.INFO)

async def test_debate():
    """Test agents debating React vs Vue."""
    
    # Create swarm with unique channel
    channel = f"debate-{uuid.uuid4().hex[:8]}"
    swarm = Swarm(channel=channel)
    
    print(f"Starting debate in #{channel}")
    
    # Give debate topic
    await swarm.send_human_message("Debate: React vs Vue for frontend. Each agent pick a side and argue. Respond to each other's points.")
    
    # Stagger agent spawning so they can respond to each other
    print("Spawning zealot...")
    await swarm.spawn_agent("zealot")
    await asyncio.sleep(5)  # Let zealot respond first
    
    print("Spawning sentinel...")  
    await swarm.spawn_agent("sentinel")
    await asyncio.sleep(5)  # Let sentinel see zealot's response
    
    print("Spawning harbinger...")
    await swarm.spawn_agent("harbinger")
    await asyncio.sleep(10)  # Let them all debate
    
    # Show the conversation
    conversation = swarm.get_conversation(channel)
    print(f"\n=== DEBATE IN #{channel} ===")
    for msg in conversation:
        print(f"{msg['sender']}: {msg['content'][:200]}...")

if __name__ == "__main__":
    asyncio.run(test_debate())