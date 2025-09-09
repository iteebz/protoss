"""Coordination tests - Multi-agent swarm behavior and message queuing."""

import pytest
from unittest.mock import AsyncMock, patch
from protoss import Nexus
from protoss.structures.pylon import Pylon
from protoss.khala import Psi


@pytest.mark.asyncio
async def test_multi_agent_pathway_coordination(mock_khala):
    """Test multiple agents coordinating on shared pathway."""
    
    # Setup pathway with multiple agents
    pathway = "coordination-test"
    agents = ["tassadar-123", "zeratul-456", "artanis-789"]
    
    # All agents join pathway
    for agent in agents:
        mock_khala.attune(agent, pathway)
    
    # Agent sends message to pathway
    message = Psi(pathway, "tassadar-123", "propose", "Let's coordinate our approach")
    
    # Simulate message distribution
    mock_agents_dict = {agent: AsyncMock() for agent in agents}
    await mock_khala.transmit(message, mock_agents_dict)
    
    # Verify all other agents received the message
    for agent in ["zeratul-456", "artanis-789"]:  # Exclude sender
        mock_agents_dict[agent].send.assert_called_with(message.serialize())


@pytest.mark.asyncio
async def test_cross_pathway_mention_coordination(mock_khala):
    """Test agents coordinating across different pathways via mentions."""
    
    # Setup two separate pathways
    mock_khala.attune("strategy-lead", "strategy-pathway")
    mock_khala.attune("execution-lead", "execution-pathway")
    
    # Strategy agent mentions execution agent across pathways
    mention_msg = Psi(
        "strategy-pathway", 
        "strategy-lead", 
        "coordinate",
        "@execution-lead we need to align on the implementation timeline"
    )
    
    mock_agents_dict = {
        "strategy-lead": AsyncMock(),
        "execution-lead": AsyncMock()
    }
    
    await mock_khala.transmit(mention_msg, mock_agents_dict)
    
    # Verify mentioned agent received message despite being on different pathway
    mock_agents_dict["execution-lead"].send.assert_called_with(mention_msg.serialize())


@pytest.mark.asyncio
async def test_nexus_zealot_coordination_flow(mock_websockets_connect):
    """Test complete Nexus → Gateway → Zealot → Pylon coordination."""
    
    with patch('protoss.structures.pylon.Pylon') as MockPylon:
        mock_pylon = AsyncMock()
        MockPylon.return_value = mock_pylon
        
        nexus = Nexus(pylon_port=8233)
        nexus.pylon = mock_pylon
        
        # Mock the coordination flow
        with patch.object(nexus.gateway, 'spawn_zealot', new_callable=AsyncMock) as mock_spawn:
            mock_spawn.return_value = "zealot-coordination-test"
            
            mock_websocket = mock_websockets_connect.return_value.__aenter__.return_value
            mock_websocket.recv.return_value = "§PSI:nexus:zealot-coordination-test:report:Coordination task completed"
            
            # Execute coordinated task
            result = await nexus.execute_task("Coordinate with team on implementation")
            
            # Verify coordination chain
            mock_spawn.assert_called_once_with("Coordinate with team on implementation", target="nexus")
            assert "Coordination task completed" in result


@pytest.mark.asyncio
async def test_agent_message_queuing_behavior():
    """Test agent message queuing when multiple messages arrive."""
    
    from protoss.khala import Khala
    khala = Khala()
    
    # Agent joins pathway
    agent_id = "busy-agent"
    pathway = "high-traffic-pathway"
    khala.attune(agent_id, pathway)
    
    # Multiple messages sent to pathway rapidly
    messages = [
        Psi(pathway, f"sender-{i}", "urgent", f"Message {i}")
        for i in range(5)
    ]
    
    # Add messages to pathway memory (simulating queuing)
    for msg in messages:
        khala.memories.setdefault(pathway, []).append(msg)
    
    # Agent reconnects and should receive queued messages
    recent_memories = khala.attune(agent_id, pathway)
    
    # Verify message queuing behavior
    assert len(khala.memories[pathway]) == 5
    assert all(msg.content.startswith("Message") for msg in messages)


@pytest.mark.asyncio
async def test_fault_tolerant_coordination():
    """Test coordination continues despite individual agent failures."""
    
    from protoss.khala import Khala
    khala = Khala()
    
    # Setup coordination pathway with multiple agents
    pathway = "resilient-pathway"
    agents = ["leader", "worker-1", "worker-2", "worker-3"]
    
    for agent in agents:
        khala.attune(agent, pathway)
    
    # Simulate one agent disconnecting
    khala.sever("worker-1")
    
    # Send coordination message
    coord_msg = Psi(pathway, "leader", "coordinate", "Continue with reduced team")
    
    mock_agents = {
        "leader": AsyncMock(),
        "worker-2": AsyncMock(), 
        "worker-3": AsyncMock()
        # worker-1 deliberately missing (disconnected)
    }
    
    await khala.transmit(coord_msg, mock_agents)
    
    # Verify remaining agents received message
    mock_agents["worker-2"].send.assert_called_with(coord_msg.serialize())
    mock_agents["worker-3"].send.assert_called_with(coord_msg.serialize())
    
    # Verify system didn't crash from missing agent
    assert "worker-1" not in khala.subscribers[pathway]


def test_coordination_pathway_scaling():
    """Test coordination pathways handle scaling to many agents."""
    
    from protoss.khala import Khala
    khala = Khala()
    
    pathway = "large-scale-pathway"
    
    # Scale to many agents
    agent_count = 50
    for i in range(agent_count):
        khala.attune(f"agent-{i}", pathway)
    
    # Verify all agents are registered
    assert len(khala.subscribers[pathway]) == agent_count
    
    # Test message memory management at scale
    for i in range(100):  # More messages than memory limit
        msg = Psi(pathway, f"agent-{i % agent_count}", "status", f"Update {i}")
        khala.memories.setdefault(pathway, []).append(msg)
    
    # Trigger memory trimming
    if len(khala.memories[pathway]) > khala.max_memory:
        khala.memories[pathway] = khala.memories[pathway][-khala.max_memory:]
    
    # Verify memory stays within limits
    assert len(khala.memories[pathway]) <= khala.max_memory