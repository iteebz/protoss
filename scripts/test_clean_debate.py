#!/usr/bin/env python3
"""Test pure constitutional debate without role instructions."""

import asyncio
import logging
import uuid
from src.protoss.swarm import Swarm

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def test_clean_debate():
    """Test agents debating with pure constitutional identities."""
    
    channel = f"clean-{uuid.uuid4().hex[:8]}"
    swarm = Swarm(channel=channel)
    
    print(f"Clean debate in #{channel}")
    
    # Pure topic, no role instructions
    await swarm.send_human_message("""
Should we rewrite our entire codebase in Rust for performance? 
Debate until you reach consensus or agree to disagree, then signal !consensus.
""")
    
    # Start all agents - let constitutional identities emerge naturally
    await swarm.start()
    
    # Wait for natural conclusion
    await asyncio.sleep(30)
    
    # Show the constitutional debate
    conversation = swarm.get_conversation(channel)
    
    print(f"\n=== CONSTITUTIONAL DEBATE ===")
    for msg in conversation:
        sender = msg['sender'].upper() if msg['sender'] != 'human' else 'HUMAN'
        content = msg['content'][:300] + "..." if len(msg['content']) > 300 else msg['content']
        print(f"\n{sender}: {content}")
    
    # Check for consensus signals
    consensus_signals = [msg for msg in conversation if "!consensus" in msg['content'].lower()]
    print(f"\nConsensus signals: {len(consensus_signals)}")

if __name__ == "__main__":
    asyncio.run(test_clean_debate())