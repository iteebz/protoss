#!/usr/bin/env python3
"""Test agents building something real together."""

import asyncio
import logging
import uuid
from src.protoss.swarm import Swarm

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def test_build_task():
    """Test agents building a real project through coordination."""
    
    run_id = uuid.uuid4().hex[:8]
    channel = f"build-{run_id}"
    base_dir = f"./test-run-{run_id}"
    
    swarm = Swarm(channel=channel, base_dir=base_dir)
    
    print(f"Build coordination in #{channel} using sandbox: {base_dir}")
    
    # Real building task
    await swarm.send_human_message("""
Build a simple calculator web app with the following features:
- HTML frontend with buttons for numbers and operations (+, -, *, /)
- Basic styling to make it look decent  
- JavaScript to handle calculations
- All in a single HTML file

Coordinate who does what, build it, and test that it works. Signal !complete when done.
""")
    
    # Start the swarm
    await swarm.start()
    
    # Wait for coordination and building
    await asyncio.sleep(60)  # Give them time to build
    
    # Show the coordination conversation
    conversation = swarm.get_conversation(channel)
    
    print(f"\n=== BUILD COORDINATION ===")
    for msg in conversation:
        sender = msg['sender'].upper() if msg['sender'] != 'human' else 'HUMAN'
        content = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
        print(f"\n{sender}: {content}")
    
    # Check for completion signals
    complete_signals = [msg for msg in conversation if "!complete" in msg['content'].lower()]
    print(f"\nCompletion signals: {len(complete_signals)}")

if __name__ == "__main__":
    asyncio.run(test_build_task())