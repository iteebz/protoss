"""Test pure conversational coordination."""

import asyncio
import pytest
from src.protoss.swarm import Swarm


@pytest.mark.asyncio
async def test_two_agent_coordination():
    """Test that two agents can coordinate through conversation."""
    swarm = Swarm()
    
    # Spawn two agents
    await swarm.spawn_agent("claude")
    await swarm.spawn_agent("gemini")
    
    # Give human task
    await swarm.send_human_message("Please create a simple todo app. One agent handle backend, one handle frontend.")
    
    # Wait for coordination
    await swarm.wait_for_completion(timeout=60.0)
    
    # Check conversation
    conversation = swarm.get_conversation()
    
    # Should have messages from both agents
    claude_messages = [msg for msg in conversation if msg["sender"] == "claude"]
    gemini_messages = [msg for msg in conversation if msg["sender"] == "gemini"]
    
    assert len(claude_messages) > 0, "Claude should have responded"
    assert len(gemini_messages) > 0, "Gemini should have responded"
    
    # Should show coordination
    all_content = " ".join([msg["content"].lower() for msg in conversation])
    assert any(word in all_content for word in ["backend", "frontend", "database"]), "Should discuss task division"


@pytest.mark.asyncio  
async def test_agent_despawn():
    """Test that agents can despawn through conversation."""
    swarm = Swarm()
    
    await swarm.spawn_agent("claude")
    await swarm.send_human_message("Say hello then despawn with !despawn")
    
    await swarm.wait_for_completion(timeout=30.0)
    
    conversation = swarm.get_conversation()
    despawn_messages = [msg for msg in conversation if "!despawn" in msg["content"].lower()]
    
    assert len(despawn_messages) > 0, "Agent should have despawned"


if __name__ == "__main__":
    # Run test manually
    asyncio.run(test_two_agent_coordination())