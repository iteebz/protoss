#!/usr/bin/env python3
"""
KHALA NETWORK INTEGRITY TEST

Tests PSI message routing, pathway persistence, agent connection patterns.
LIVE FIRE: Real WebSocket connections, actual message routing.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.pylon import Pylon
from protoss.structures.gateway import Gateway
from protoss.khala import Khala, Psi


async def test_khala_basic_routing():
    """Test basic PSI message routing between agents."""
    print("🔹 TESTING: Basic Khala PSI routing")
    
    # Start Pylon infrastructure
    pylon = Pylon(8889)  # Use different port to avoid conflicts
    await pylon.start()
    print("🔹 Pylon online for testing")
    
    try:
        # Connect two mock agents to Khala
        khala1 = Khala()
        khala1.set_grid_port(8889)
        
        khala2 = Khala()
        khala2.set_grid_port(8889)
        
        # Test message routing
        async with khala1.connect("test-agent-1") as conn1:
            async with khala2.connect("test-agent-2") as conn2:
                
                # Agent 1 sends to pathway
                test_message = Psi(
                    pathway="test-pathway",
                    sender="test-agent-1", 
                    content="Hello from agent 1"
                )
                
                await conn1.send("test-pathway", "Hello from agent 1")
                print("✅ Message sent to test-pathway")
                
                # Small delay for message propagation
                await asyncio.sleep(0.5)
                
                # Verify pathway has message
                memories = khala1.memories.get("test-pathway", [])
                if memories:
                    print(f"✅ Pathway has {len(memories)} messages")
                    print(f"   Latest: {memories[-1].content}")
                else:
                    print("❌ No messages found in pathway")
                
    finally:
        await pylon.stop()
        print("🔹 Test Pylon stopped")


async def test_agent_connection_lifecycle():
    """Test agent connection, disconnection, and memory persistence."""
    print("\n🔹 TESTING: Agent connection lifecycle")
    
    pylon = Pylon(8890)
    await pylon.start()
    
    try:
        khala = Khala()
        khala.set_grid_port(8890)
        
        # Connect agent, send message, disconnect
        async with khala.connect("lifecycle-agent") as conn:
            await conn.send("lifecycle-test", "Message before disconnect")
        
        print("✅ Agent connected, sent message, disconnected")
        
        # Reconnect and check memory persistence
        async with khala.connect("lifecycle-agent") as conn:
            memories = khala.memories.get("lifecycle-test", [])
            if memories and memories[-1].content == "Message before disconnect":
                print("✅ Message persisted across reconnection")
            else:
                print("❌ Message lost on reconnection")
                
    finally:
        await pylon.stop()


async def test_concurrent_agents():
    """Test multiple agents communicating simultaneously."""
    print("\n🔹 TESTING: Concurrent agent communication")
    
    pylon = Pylon(8891) 
    await pylon.start()
    
    try:
        # Create multiple Khala connections
        tasks = []
        
        async def agent_task(agent_id: str, message_count: int):
            khala = Khala()
            khala.set_grid_port(8891)
            
            async with khala.connect(agent_id) as conn:
                for i in range(message_count):
                    await conn.send("concurrent-test", f"Message {i} from {agent_id}")
                    await asyncio.sleep(0.1)
        
        # Launch 3 agents sending messages concurrently
        tasks = [
            agent_task("agent-alpha", 3),
            agent_task("agent-beta", 3), 
            agent_task("agent-gamma", 3)
        ]
        
        await asyncio.gather(*tasks)
        print("✅ All agents completed concurrent messaging")
        
        # Check final message count
        khala = Khala()
        khala.set_grid_port(8891)
        memories = khala.memories.get("concurrent-test", [])
        print(f"✅ Total messages in pathway: {len(memories)}")
        
        if len(memories) == 9:  # 3 agents × 3 messages each
            print("✅ All concurrent messages received")
        else:
            print(f"❌ Expected 9 messages, got {len(memories)}")
            
    finally:
        await pylon.stop()


async def main():
    """Run all Khala network integrity tests."""
    print("🔮 KHALA NETWORK INTEGRITY TEST - LIVE FIRE")
    print("=" * 50)
    
    try:
        await test_khala_basic_routing()
        await test_agent_connection_lifecycle() 
        await test_concurrent_agents()
        
        print("\n🔮 KHALA NETWORK TESTS COMPLETE")
        
    except Exception as e:
        print(f"\n❌ KHALA TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())