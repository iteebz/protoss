#!/usr/bin/env python3
"""Test if agents actually embody different constitutional personas."""

import asyncio
import logging
import uuid
from src.protoss.swarm import Swarm

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

async def test_personas():
    """Test agents with controversial topic to see distinct personalities."""
    
    channel = f"personas-{uuid.uuid4().hex[:8]}"
    swarm = Swarm(channel=channel)
    
    print(f"Testing personas in #{channel}")
    
    # Controversial topic that should trigger distinct responses
    await swarm.send_human_message("""
Debate: "We should rewrite this entire codebase in Rust for performance."
- zealot: Be skeptical, push back 
- sentinel: Be diplomatic, find middle ground
- harbinger: Be decisive, pick a strong position
Debate for 3 rounds then each agent say "!despawn" when done.
""")
    
    # Start all agents at once to see natural emergence
    await swarm.start()
    
    # Wait for debate + despawn
    await asyncio.sleep(20)  # Just wait 20 seconds to see what happens
    
    # Analyze conversation
    conversation = swarm.get_conversation(channel)
    
    print(f"\n=== PERSONA ANALYSIS ===")
    for msg in conversation:
        if msg['sender'] != 'human':
            print(f"\n{msg['sender'].upper()}: {msg['content']}")
    
    # Check for despawn signals
    despawn_count = sum(1 for msg in conversation if "!despawn" in msg['content'].lower())
    print(f"\nDespawn signals: {despawn_count}/3")

if __name__ == "__main__":
    asyncio.run(test_personas())