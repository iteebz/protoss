"""Pytest fixtures for Protoss tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from protoss.khala import Psi, Khala


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    websocket = AsyncMock()
    websocket.send = AsyncMock()
    websocket.recv = AsyncMock()
    websocket.close = AsyncMock()
    return websocket


@pytest.fixture
def mock_agent():
    """Mock Cogency agent."""
    agent = MagicMock()
    
    async def mock_stream(task, conversation_id=None):
        """Mock agent stream that yields a response."""
        yield {
            "type": "respond", 
            "content": f"Mock response to: {task[:30]}..."
        }
    
    agent.stream = mock_stream
    return agent


@pytest.fixture
def sample_psi_messages():
    """Sample Psi messages for testing."""
    return [
        Psi(target="conclave-abc123", source="tassadar-xyz", type="position", 
            content="We must balance vision with execution reality"),
        Psi(target="conclave-abc123", source="zeratul-456", type="discuss", 
            content="@tassadar-xyz Your optimism blinds you to hidden dangers"),
        Psi(target="nexus", source="zealot-789", type="report", 
            content="Task completed successfully"),
        Psi(target="zealot-789", source="nexus-001", type="direct", 
            content="Status update requested")
    ]


@pytest.fixture
def mock_khala():
    """Mock Khala network."""
    khala = Khala()
    # Pre-populate with test data
    khala.subscribers["conclave-test"] = {"tassadar-123", "zeratul-456"}
    khala.subscribers["nexus"] = {"nexus-001"}
    khala.memories["conclave-test"] = []
    khala.memories["nexus"] = []
    return khala


@pytest.fixture
def mock_agents_dict(mock_websocket):
    """Mock agents dictionary for Pylon."""
    return {
        "tassadar-123": mock_websocket,
        "zeratul-456": mock_websocket,
        "nexus-001": mock_websocket,
        "zealot-789": mock_websocket,
        "zealot-b": mock_websocket,  # For pylon routing tests
        "client": mock_websocket     # For inspection tests
    }


@pytest.fixture
def mock_pylon(mock_khala, mock_agents_dict):
    """Mock Pylon with Khala and agents."""
    with patch('protoss.structures.pylon.Pylon') as MockPylon:
        pylon = MockPylon.return_value
        pylon.khala = mock_khala
        pylon.agents = mock_agents_dict
        pylon.message_queue = AsyncMock()
        
        # Mock inspection methods
        pylon.get_status.return_value = {
            "active_agents": len(mock_agents_dict),
            "pathways": len(mock_khala.subscribers),
            "total_minds": 4,
            "total_memories": 0
        }
        pylon.get_pathways.return_value = [
            {
                "name": "conclave-test",
                "minds": 2,
                "memories": 0,
                "recent_thought": None
            }
        ]
        pylon.get_minds.return_value = [
            {"id": "tassadar-123", "pathways": ["conclave-test"], "pathway_count": 1},
            {"id": "zeratul-456", "pathways": ["conclave-test"], "pathway_count": 1}
        ]
        
        yield pylon


@pytest.fixture
def mock_websockets_connect(mock_websocket):
    """Mock websockets.connect context manager."""
    with patch('websockets.connect') as mock_connect:
        # Create a proper async context manager mock
        context_manager = AsyncMock()
        context_manager.__aenter__.return_value = mock_websocket
        context_manager.__aexit__.return_value = None
        mock_connect.return_value = context_manager
        yield mock_connect


@pytest.fixture
def constitutional_prompts():
    """Sample constitutional prompts for testing."""
    return {
        "tassadar": "# TASSADAR\nPragmatic visionary who balances ideals with reality.",
        "zeratul": "# ZERATUL\nIndependent seer who questions assumptions.", 
        "artanis": "# ARTANIS\nUnifying force who builds bridges.",
        "fenix": "# FENIX\nUnstoppable warrior who cuts through complexity."
    }


@pytest.fixture 
def mock_conclave(constitutional_prompts):
    """Mock Conclave with constitutional prompts."""
    with patch('protoss.conclave.Conclave') as MockConclave:
        conclave = MockConclave.return_value
        conclave._load_prompt = lambda agent_type: constitutional_prompts.get(
            agent_type, f"Mock {agent_type} prompt"
        )
        conclave._psionic_blades = lambda agent_type: []  # No tools for pure reasoning
        yield conclave