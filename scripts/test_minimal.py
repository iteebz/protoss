#!/usr/bin/env python3
"""Minimal test of conversational coordination."""

import asyncio
import logging
from src.protoss.swarm import Swarm

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def test_coordination():
    """Test 3 agents coordinating through conversation."""
    
    # Create swarm
    swarm = Swarm()
    
    # Start 3 constitutional agents
    await swarm.start()
    
    # Give them a task
    await swarm.send_human_message("Please create a simple todo app with backend and frontend. Coordinate who does what.")
    
    # Let them coordinate for 10 seconds to see initial responses  
    print("Watching agents coordinate...")
    await asyncio.sleep(10.0)  # Just wait 10 seconds then check conversation
    
    # Show the conversation
    conversation = swarm.get_conversation()
    print("\n=== CONVERSATION ===")
    for msg in conversation:
        print(f"{msg['sender']}: {msg['content']}")

if __name__ == "__main__":
    asyncio.run(test_coordination())