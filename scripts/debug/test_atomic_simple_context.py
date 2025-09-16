#!/usr/bin/env python3
"""
TEST COGENCY CONVERSATION ID PATTERNS

Test if specific conversation IDs or content types cause persistence failures.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.gateway import Gateway


async def test_conversation_patterns():
    """Test different conversation ID patterns."""
    print("🧠 ATOMIC TEST: Cogency conversation persistence patterns")
    
    gateway = Gateway()
    
    # Test different conversation ID patterns
    test_cases = [
        ("Simple ID", "simple-test", "What is JWT?"),
        ("Position suffix", "test-pos", "What is JWT?"),  # This pattern failed before
        ("Complex content", "simple-test", """
Original question: Should we use JWT tokens or server-side sessions?

Tassadar's position:
JWT tokens provide stateless authentication which scales better for distributed systems.

Respond as Zeratul with your constitutional perspective.
"""),
        ("Single line context", "test-context", "Original question: Should we use JWT? Tassadar says JWT is better. Respond as Zeratul.")
    ]
    
    for name, conv_id, prompt in test_cases:
        print(f"\n🔹 Test: {name}")
        print(f"   Conversation ID: {conv_id}")
        print(f"   Prompt length: {len(prompt)} chars")
        
        try:
            # Create fresh agent for each test
            zeratul = gateway.spawn("zeratul")
            
            # Override conversation ID pattern used by deliberate method
            # We need to examine how agents set conversation IDs
            result = ""
            agent_stream = zeratul.agent(prompt, conversation_id=conv_id)
            
            try:
                async for event in agent_stream:
                    if event.get("type") == "respond":
                        result = event.get("content", "")
                        break
            finally:
                await agent_stream.aclose()
                
            if result:
                print(f"   ✅ Success: {result[:50]}...")
            else:
                print(f"   ❌ No result returned")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print(f"\n🧠 Conversation persistence pattern test complete")


if __name__ == "__main__":
    asyncio.run(test_conversation_patterns())