#!/usr/bin/env python3
"""
ATOMIC KHALA MESSAGING TEST

Can two agents send messages via Khala network?
Minimal infrastructure: Pylon + 2 agents + simple message exchange.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.pylon import Pylon
from protoss.khala import Khala


async def test_simple_khala_messaging():
    """Test basic Khala message routing between two mock agents."""
    print("🔹 ATOMIC TEST: Simple Khala messaging")
    
    # Start Pylon infrastructure
    pylon = Pylon(8950)  # Use unique port
    await pylon.start()
    print("🔹 Pylon online")
    
    try:
        # Connect two agents to Khala
        khala = Khala()
        khala.set_grid_port(8950)
        
        async with khala.connect("test-agent-1") as conn1:
            async with khala.connect("test-agent-2") as conn2:
                
                print("🔹 Both agents connected")
                
                # Agent 1 sends message to shared pathway
                await conn1.send("test-pathway", "Hello from agent 1")
                print("✅ Agent 1 sent message")
                
                # Small delay for message propagation
                await asyncio.sleep(0.5)
                
                # Check if message was stored in Khala memory
                memories = khala.memories.get("test-pathway", [])
                if memories:
                    print(f"✅ Message stored in Khala: {memories[-1].content}")
                else:
                    print("❌ No message found in Khala memory")
                
                # Agent 2 sends response
                await conn2.send("test-pathway", "Hello from agent 2") 
                print("✅ Agent 2 sent response")
                
                await asyncio.sleep(0.5)
                
                # Check final message count
                memories = khala.memories.get("test-pathway", [])
                print(f"✅ Total messages in pathway: {len(memories)}")
                
                for i, msg in enumerate(memories):
                    print(f"   {i+1}. {msg.sender}: {msg.content}")
                    
    finally:
        await pylon.stop()
        print("🔹 Pylon stopped")


if __name__ == "__main__":
    asyncio.run(test_simple_khala_messaging())