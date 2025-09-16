#!/usr/bin/env python3
"""
ATOMIC CONTEXT TEST

Can a single agent handle complex context prompts?
Isolate the Cogency conversation state issue.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.gateway import Gateway


async def test_agent_context_handling():
    """Test agent handling complex context prompts."""
    print("🧠 ATOMIC TEST: Agent context handling")
    
    gateway = Gateway()
    zeratul = gateway.spawn("zeratul")
    
    print(f"🔍 Testing {zeratul.id}")
    
    # Test 1: Simple prompt (should work)
    print("\n🔹 Test 1: Simple prompt")
    simple = "What is JWT authentication?"
    
    try:
        result = await zeratul.deliberate(simple)
        print(f"✅ Simple: {result[:100]}...")
    except Exception as e:
        print(f"❌ Simple failed: {e}")
    
    # Test 2: Complex context prompt (may fail)
    print("\n🔹 Test 2: Complex context prompt")
    complex_prompt = f"""
Original question: Should we use JWT tokens or server-side sessions?

Tassadar's position:
JWT tokens provide stateless authentication which scales better for distributed systems. They allow for horizontal scaling without session affinity requirements.

Provide your constitutional perspective as Zeratul, responding to Tassadar's position.
Be direct about where you agree/disagree.
"""
    
    try:
        result = await zeratul.deliberate(complex_prompt)
        print(f"✅ Complex: {result[:100]}...")
    except Exception as e:
        print(f"❌ Complex failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Even simpler context
    print("\n🔹 Test 3: Minimal context")
    minimal = "Respond to this: 'JWT tokens are better than sessions.'"
    
    try:
        result = await zeratul.deliberate(minimal)
        print(f"✅ Minimal: {result[:100]}...")
    except Exception as e:
        print(f"❌ Minimal failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_agent_context_handling())