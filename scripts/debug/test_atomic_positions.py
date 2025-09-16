#!/usr/bin/env python3
"""
ATOMIC SACRED FOUR POSITION TEST

Just test: Can we get 4 different constitutional perspectives on same question?
No Khala. No deliberation. No infrastructure. Just agents reasoning.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.gateway import Gateway


async def test_sacred_four_positions():
    """Test Sacred Four can form independent positions on same question."""
    print("🔮 ATOMIC TEST: Sacred Four position formation")
    
    question = "Should we use JWT tokens or server-side sessions for authentication?"
    
    gateway = Gateway()
    
    # Spawn Sacred Four
    tassadar = gateway.spawn("tassadar")
    zeratul = gateway.spawn("zeratul") 
    artanis = gateway.spawn("artanis")
    fenix = gateway.spawn("fenix")
    
    sacred_four = {
        "tassadar": tassadar,
        "zeratul": zeratul,
        "artanis": artanis, 
        "fenix": fenix
    }
    
    print(f"📋 Question: {question}")
    print("⚡ Sacred Four forming positions...")
    
    positions = {}
    
    # Test each agent independently
    for name, agent in sacred_four.items():
        print(f"\n💭 {name} deliberating...")
        
        try:
            if hasattr(agent, 'deliberate'):
                position = await agent.deliberate(question)
                positions[name] = position
                print(f"✅ {name}: {position[:100]}...")
            else:
                positions[name] = f"ERROR: No deliberate method"
                print(f"❌ {name}: Missing deliberate method")
                
        except Exception as e:
            positions[name] = f"ERROR: {e}"
            print(f"❌ {name} failed: {e}")
    
    print(f"\n🔮 RESULTS:")
    print(f"   Successful positions: {sum(1 for p in positions.values() if not p.startswith('ERROR'))}/4")
    
    # Show constitutional diversity
    for name, position in positions.items():
        if not position.startswith('ERROR'):
            print(f"\n{name.upper()}:")
            print(f"   {position[:200]}...")
    
    return positions


if __name__ == "__main__":
    asyncio.run(test_sacred_four_positions())