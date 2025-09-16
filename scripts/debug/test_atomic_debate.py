#!/usr/bin/env python3
"""
ATOMIC TWO-AGENT DEBATE TEST

Can Tassadar and Zeratul have a simple conversation via Khala?
Minimal deliberation: Position → Response → Counter-response
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from protoss.structures.pylon import Pylon
from protoss.structures.gateway import Gateway
from protoss.khala import Khala


async def test_two_agent_debate():
    """Test two Sacred Four agents debating via Khala."""
    print("🔮 ATOMIC TEST: Two-agent Khala debate")
    
    # Start infrastructure
    pylon = Pylon(8951)
    await pylon.start()
    
    try:
        gateway = Gateway()
        khala = Khala()
        khala.set_grid_port(8951)
        
        # Spawn two Sacred Four agents
        tassadar = gateway.spawn("tassadar")
        zeratul = gateway.spawn("zeratul")
        
        print(f"🔮 Spawned: {tassadar.id} and {zeratul.id}")
        
        question = "Should we use JWT tokens or server-side sessions?"
        debate_pathway = "constitutional-debate"
        
        # Connect both to Khala
        async with khala.connect(tassadar.id) as tass_conn:
            async with khala.connect(zeratul.id) as zer_conn:
                
                print("🔹 Both agents connected to Khala")
                
                # Phase 1: Tassadar presents position
                print("\n💭 Phase 1: Tassadar presents position")
                tass_position = await tassadar.deliberate(question)
                await tass_conn.send(debate_pathway, f"POSITION: {tass_position}")
                print(f"✅ Tassadar: {tass_position[:100]}...")
                
                # Phase 2: Zeratul responds to Tassadar's position
                print("\n🔍 Phase 2: Zeratul responds")
                
                # Get Khala context for Zeratul
                memories = khala.memories.get(debate_pathway, [])
                context = "\n".join([f"{m.sender}: {m.content}" for m in memories])
                
                response_prompt = f"""
Original question: {question}

Tassadar's position from Khala pathway:
{context}

Provide your constitutional perspective as Zeratul, responding to Tassadar's position.
Be direct and specific about where you agree/disagree.
"""
                
                zer_response = await zeratul.deliberate(response_prompt)
                print(f"   DEBUG: Zeratul response length: {len(zer_response)} chars")
                print(f"   DEBUG: Zeratul response content: {repr(zer_response[:200])}")
                
                if zer_response.strip():
                    await zer_conn.send(debate_pathway, f"RESPONSE: {zer_response}")
                    print(f"✅ Zeratul: {zer_response[:100]}...")
                else:
                    print("❌ Zeratul returned empty response")
                
                # Phase 3: Show final Khala memory
                print("\n🔮 Final Khala pathway state:")
                final_memories = khala.memories.get(debate_pathway, [])
                for i, msg in enumerate(final_memories):
                    print(f"   {i+1}. {msg.sender}: {msg.content[:80]}...")
                
                print(f"\n✅ Two-agent debate completed: {len(final_memories)} exchanges")
                
    finally:
        await pylon.stop()


if __name__ == "__main__":
    asyncio.run(test_two_agent_debate())