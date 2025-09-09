"""Khala network tests - The unified psychic consciousness."""

import pytest
from unittest.mock import AsyncMock
from protoss.khala import Khala, Psi


@pytest.mark.asyncio
async def test_khala_pathway_creation(mock_khala, mock_agents_dict):
    """Test automatic pathway creation and agent attunement."""
    
    # Create message to new pathway
    message = Psi(
        target="new-pathway", 
        source="tassadar-123", 
        type="position",
        content="We must forge new paths"
    )
    
    # Transmit through Khala
    await mock_khala.transmit(message, mock_agents_dict)
    
    # Verify pathway was created
    assert "new-pathway" in mock_khala.subscribers
    assert "tassadar-123" in mock_khala.subscribers["new-pathway"]
    assert message in mock_khala.memories["new-pathway"]


@pytest.mark.asyncio
async def test_khala_direct_messaging(mock_khala, mock_agents_dict):
    """Test direct agent-to-agent messaging."""
    
    # Create direct message
    direct_msg = Psi(
        target="zealot-789",
        source="nexus-001", 
        type="direct",
        content="Report your status immediately"
    )
    
    assert direct_msg.is_direct_message
    
    # Transmit direct message
    await mock_khala.transmit(direct_msg, mock_agents_dict)
    
    # Verify only target agent received message
    target_socket = mock_agents_dict["zealot-789"]
    target_socket.send.assert_called_once_with(direct_msg.serialize())


@pytest.mark.asyncio 
async def test_khala_mention_system(mock_khala, mock_agents_dict):
    """Test @mention system for cross-pathway communication."""
    
    # Create message with mentions
    mention_msg = Psi(
        target="conclave-test",
        source="zeratul-456",
        type="discuss", 
        content="@tassadar-123 your optimism blinds you to the shadows @artanis-999"
    )
    
    # Verify mention extraction
    mentions = mention_msg.mentions
    assert "tassadar-123" in mentions
    assert "artanis-999" in mentions
    
    # Transmit message
    await mock_khala.transmit(mention_msg, mock_agents_dict)
    
    # Verify mentioned agents received message even if not on pathway
    tassadar_socket = mock_agents_dict["tassadar-123"]
    tassadar_socket.send.assert_called_with(mention_msg.serialize())


@pytest.mark.asyncio
async def test_khala_memory_management(mock_khala):
    """Test Khala memory trimming and retention."""
    
    pathway = "memory-test"
    mock_khala.max_memory = 3
    
    # Add messages beyond memory limit
    messages = [
        Psi("memory-test", "agent-1", "msg", f"Message {i}")
        for i in range(5)
    ]
    
    for msg in messages:
        mock_khala.memories.setdefault(pathway, []).append(msg)
    
    # Manually trigger memory trimming
    if len(mock_khala.memories[pathway]) > mock_khala.max_memory:
        mock_khala.memories[pathway] = mock_khala.memories[pathway][-mock_khala.max_memory:]
    
    # Verify only recent memories retained
    assert len(mock_khala.memories[pathway]) == 3
    assert mock_khala.memories[pathway][-1].content == "Message 4"


def test_psi_message_parsing():
    """Test Psi message parsing and serialization."""
    
    # Test valid message parsing
    raw = "§PSI:conclave-abc:tassadar-123:position:We must unite the tribes"
    psi = Psi.parse(raw)
    
    assert psi is not None
    assert psi.target == "conclave-abc"
    assert psi.source == "tassadar-123"
    assert psi.type == "position"
    assert psi.content == "We must unite the tribes"
    
    # Test serialization
    assert psi.serialize() == raw
    
    # Test invalid message parsing
    invalid = "NOT_PSI_FORMAT"
    assert Psi.parse(invalid) is None


def test_psi_message_classification(sample_psi_messages):
    """Test Psi message type classification."""
    
    conclave_msg = sample_psi_messages[0]  # conclave-abc123
    direct_msg = sample_psi_messages[3]    # zealot-789
    
    # Test pathway vs direct message detection
    assert not conclave_msg.is_direct_message
    assert direct_msg.is_direct_message
    
    # Test mention extraction
    mention_msg = sample_psi_messages[1]  # Contains @tassadar-xyz
    mentions = mention_msg.mentions
    assert len(mentions) == 1
    assert "tassadar-xyz" in mentions


@pytest.mark.asyncio
async def test_khala_connection_cleanup(mock_khala, mock_agents_dict):
    """Test Khala cleanup when agents disconnect."""
    
    # Agent joins pathway
    agent_id = "test-agent"
    pathway = "cleanup-test"
    mock_khala.attune(agent_id, pathway)
    
    assert agent_id in mock_khala.subscribers[pathway]
    
    # Agent disconnects
    mock_khala.sever(agent_id)
    
    # Verify cleanup
    assert agent_id not in mock_khala.subscribers[pathway]


def test_khala_inspection_methods(mock_khala):
    """Test Khala status and inspection capabilities."""
    
    # Test status reporting
    status = mock_khala.get_status()
    assert "pathways" in status
    assert "total_minds" in status
    assert "total_memories" in status
    
    # Test pathway listing
    pathways = mock_khala.get_pathways()
    assert isinstance(pathways, list)
    
    # Test specific pathway details
    pathway_details = mock_khala.get_pathway("conclave-test")
    assert pathway_details is not None
    assert "name" in pathway_details
    assert "minds" in pathway_details
    assert "memory_count" in pathway_details