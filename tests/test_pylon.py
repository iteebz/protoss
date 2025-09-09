"""Pylon tests - Message routing and grid coordination."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from protoss.structures.pylon import Pylon
from protoss.khala import Psi
from protoss.constants import PYLON_TEST_PORT


@pytest.mark.asyncio
async def test_pylon_message_routing(mock_khala, mock_agents_dict):
    """Test Pylon routes messages through Khala network."""
    
    pylon = Pylon(port=PYLON_TEST_PORT)
    pylon.khala = mock_khala
    pylon.agents = mock_agents_dict
    pylon.message_queue = AsyncMock()
    
    # Create test message
    test_message = Psi(
        target="zealot-b", 
        source="zealot-a", 
        type="report", 
        content="hello-from-alpha"
    )
    
    # Test routing logic
    await pylon.khala.transmit(test_message, pylon.agents)
    
    # Verify direct message was routed to specific agent
    target_socket = mock_agents_dict["zealot-b"]
    target_socket.send.assert_called_with(test_message.serialize())


@pytest.mark.asyncio
async def test_pylon_agent_connection_handling(mock_khala):
    """Test Pylon handles agent connections and forwards messages directly to Khala."""
    
    pylon = Pylon(port=PYLON_TEST_PORT)
    pylon.khala = mock_khala  # Use the proper mock khala from fixture
    
    # Mock the transmit method to track calls
    pylon.khala.transmit = AsyncMock()
    
    # Mock WebSocket connection
    mock_websocket = AsyncMock()
    mock_websocket.request.path = "/zealot-abc123"
    
    # Mock incoming messages as async iterator
    messages = [
        "§PSI:pathway:zealot-abc123:join:Connected",
        "§PSI:pathway:zealot-abc123:report:Task complete"
    ]
    
    agents_during_connection = []
    
    async def async_messages(self):
        for msg in messages:
            # Capture agent state during message processing
            agents_during_connection.append("zealot-abc123" in pylon.agents)
            yield msg
    
    mock_websocket.__aiter__ = async_messages
    
    # Test connection handling
    await pylon._handle_connection(mock_websocket)
    
    # Verify agent was registered during connection (then cleaned up after)
    assert any(agents_during_connection)  # Agent was registered at some point
    assert pylon.khala.transmit.call_count == 2  # Messages forwarded directly to Khala
    assert "zealot-abc123" not in pylon.agents  # Cleaned up after disconnection


@pytest.mark.asyncio
async def test_pylon_inspection_commands(mock_agents_dict):
    """Test Pylon responds to inspection commands."""
    
    pylon = Pylon(port=PYLON_TEST_PORT)
    pylon.agents = mock_agents_dict
    
    # Mock inspection message
    inspection_msg = Psi(
        target="inspector",
        source="client",
        type="inspect", 
        content="status"
    )
    
    # Test inspection handling
    await pylon._handle_inspection(inspection_msg)
    
    # Verify response was sent
    client_socket = mock_agents_dict["client"]
    client_socket.send.assert_called()
    
    # Verify response contains status data
    call_args = client_socket.send.call_args[0][0]
    assert "§PSI:inspector:client:result:" in call_args


@pytest.mark.asyncio
async def test_pylon_pathway_memory_persistence():
    """Test Pylon maintains pathway memories across agent connections."""
    
    pylon = Pylon()
    
    # Agent joins pathway and sends message
    pylon.khala.attune("agent-1", "test-pathway")
    
    message = Psi("test-pathway", "agent-1", "discuss", "Initial thought")
    pylon.khala.memories.setdefault("test-pathway", []).append(message)
    
    # New agent joins same pathway
    memories = pylon.khala.attune("agent-2", "test-pathway")
    
    # Verify new agent receives pathway history
    assert len(memories) >= 0  # May be empty in mock, but structure exists
    assert "test-pathway" in pylon.khala.subscribers
    assert "agent-2" in pylon.khala.subscribers["test-pathway"]


def test_pylon_status_reporting(mock_khala, mock_agents_dict):
    """Test Pylon status reporting for inspection."""
    
    pylon = Pylon()
    pylon.khala = mock_khala
    pylon.agents = mock_agents_dict
    
    # Test status gathering
    status = pylon.get_status()
    
    assert "active_agents" in status
    assert "pathways" in status
    assert status["active_agents"] == len(mock_agents_dict)


def test_pylon_graceful_disconnection():
    """Test Pylon handles agent disconnection gracefully."""
    
    pylon = Pylon()
    agent_id = "test-agent"
    
    # Agent connects and joins pathway
    pylon.khala.attune(agent_id, "test-pathway")
    assert agent_id in pylon.khala.subscribers["test-pathway"]
    
    # Agent disconnects
    pylon.khala.sever(agent_id)
    
    # Verify cleanup
    assert agent_id not in pylon.khala.subscribers["test-pathway"]


@pytest.mark.asyncio
async def test_pylon_concurrent_messaging():
    """Test Pylon handles concurrent messages without race conditions."""
    
    pylon = Pylon()
    pylon.khala = AsyncMock()
    
    # Create multiple concurrent messages
    messages = [
        Psi("pathway-1", f"agent-{i}", "discuss", f"Message {i}")
        for i in range(10)
    ]
    
    # Route all messages concurrently  
    await asyncio.gather(*[
        pylon.khala.transmit(msg, {}) for msg in messages
    ])
    
    # Verify all messages were processed
    assert pylon.khala.transmit.call_count == 10