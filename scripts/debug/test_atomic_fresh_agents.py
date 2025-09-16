#!/usr/bin/env python3
"""
ATOMIC FRESH AGENT TEST

Test Sacred Four with fresh Agent instances each time (no conversation persistence).
Bypass Cogency persistence issues entirely.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.gateway import Gateway
from cogency import Agent


async def test_fresh_agent_reasoning():
    """Test agents with fresh instances each time."""
    print("🔮 ATOMIC TEST: Fresh agent reasoning (no persistence)")
    
    question = "Should we use JWT tokens or server-side sessions?"
    
    # Test 1: Fresh agent with simple question
    print("\n🔹 Test 1: Fresh Zeratul with simple question")
    agent1 = Agent(
        instructions="You are Zeratul - shadow investigation, hidden risks, skeptical analysis",
        mode="auto",  # No conversation persistence  
        llm="gemini"
    )
    
    try:
        result = ""
        agent_stream = agent1(question)
        async for event in agent_stream:
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        await agent_stream.aclose()
        
        print(f"   ✅ Success: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Fresh agent with complex context
    print("\n🔹 Test 2: Fresh Zeratul with complex context")
    agent2 = Agent(
        instructions="You are Zeratul - shadow investigation, hidden risks, skeptical analysis",
        mode="auto",
        llm="gemini" 
    )
    
    complex_context = f"""Original question: {question}

Tassadar's position: JWT tokens provide stateless authentication which scales better for distributed systems. They allow horizontal scaling without session affinity requirements.

As Zeratul, provide your constitutional perspective responding to Tassadar's position. Focus on hidden risks and what we might be missing."""
    
    try:
        result = ""
        agent_stream = agent2(complex_context)
        async for event in agent_stream:
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        await agent_stream.aclose()
        
        print(f"   ✅ Success: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    print(f"\n🔮 Fresh agent test complete - both should work without persistence issues")


if __name__ == "__main__":
    asyncio.run(test_fresh_agent_reasoning())