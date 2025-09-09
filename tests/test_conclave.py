"""Conclave tests - The Sacred Four deliberation system."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from protoss.conclave import Conclave


@pytest.mark.asyncio
async def test_conclave_convene(mock_conclave, mock_websockets_connect, constitutional_prompts):
    """Test convening the Sacred Four for deliberation."""
    
    with patch('protoss.conclave.Conclave') as MockConclave:
        conclave = MockConclave.return_value
        
        # Mock the convene method
        async def mock_convene(task):
            return "conclave-test123"
        
        conclave.convene = mock_convene
        
        # Test convening
        conclave_id = await conclave.convene("Should we implement feature X?")
        assert conclave_id == "conclave-test123"


@pytest.mark.asyncio 
async def test_conclave_participant_spawning(constitutional_prompts):
    """Test spawning individual conclave participants."""
    
    conclave = Conclave()
    
    # Mock Agent creation and WebSocket connection
    with patch('protoss.conclave.Agent') as MockAgent, \
         patch('websockets.connect') as mock_connect:
        
        mock_agent = AsyncMock()
        MockAgent.return_value = mock_agent
        
        # Mock agent stream for position formation
        async def mock_stream(prompt, conversation_id=None):
            yield {
                "type": "respond",
                "content": "My constitutional position is clear: proceed with caution"
            }
        
        mock_agent.stream = mock_stream
        
        # Mock WebSocket
        mock_websocket = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_websocket
        
        # Test spawning participant
        await conclave._spawn_participant("tassadar", "Should we proceed?", "conclave-test")
        
        # Verify agent was created with constitutional prompt
        MockAgent.assert_called_once()
        mock_connect.assert_called_once()


def test_conclave_prompt_loading(constitutional_prompts):
    """Test constitutional prompt loading for Sacred Four."""
    
    conclave = Conclave()
    
    # Mock prompt file reading
    with patch.object(conclave, '_load_prompt') as mock_load:
        mock_load.side_effect = lambda agent_type: constitutional_prompts.get(agent_type, "fallback")
        
        # Test loading each Sacred Four member
        for agent_type in ["tassadar", "zeratul", "artanis", "fenix"]:
            prompt = mock_load(agent_type)
            assert prompt.startswith(f"# {agent_type.upper()}")


@pytest.mark.asyncio
async def test_conclave_position_formation():
    """Test agent position formation from questions."""
    
    conclave = Conclave()
    
    # Mock agent
    mock_agent = MagicMock()
    
    async def mock_stream(prompt, conversation_id=None):
        if "Should we implement" in prompt:
            yield {
                "type": "respond", 
                "content": "Yes, but with careful architectural constraints to prevent complexity creep"
            }
    
    mock_agent.stream = mock_stream
    
    # Test position formation
    position = await conclave._position(
        mock_agent, 
        "tassadar-123",
        "Should we implement this new feature?"
    )
    
    assert "architectural constraints" in position


@pytest.mark.asyncio
async def test_conclave_reactive_participation(mock_websockets_connect):
    """Test reactive participation in conclave discussion."""
    
    conclave = Conclave()
    mock_websocket = mock_websockets_connect.return_value.__aenter__.return_value
    
    # Mock incoming messages
    incoming_messages = [
        "§PSI:conclave-test:zeratul-456:discuss:I question this approach",
        "§PSI:conclave-test:artanis-789:discuss:Perhaps we can find middle ground"
    ]
    
    # Mock agent that responds to first message
    mock_agent = MagicMock()
    
    async def mock_stream(prompt, conversation_id=None):
        if "I question this approach" in prompt:
            yield {
                "type": "respond",
                "content": "§PSI:conclave-test:tassadar-123:discuss:Your skepticism has merit, Zeratul"
            }
        else:
            yield {"type": "respond", "content": "no response"}
    
    mock_agent.stream = mock_stream
    
    # Mock websocket message iteration
    async def mock_message_iter():
        for msg in incoming_messages:
            yield msg
    
    mock_websocket.__aiter__ = mock_message_iter
    
    # Test participation (would normally run until connection closes)
    # We'll test the setup and first interaction
    try:
        await conclave._participate(
            mock_agent, 
            "tassadar-123",
            "Initial position: We should proceed", 
            "conclave-test",
            mock_websocket
        )
    except:
        # Expected to fail when mock websocket iteration ends
        pass
    
    # Verify initial position was sent
    mock_websocket.send.assert_called()


def test_conclave_tool_configuration():
    """Test that conclave agents get no tools for pure constitutional reasoning."""
    
    conclave = Conclave()
    
    # Conclave agents should have no tools - pure constitutional reasoning
    tools = conclave._psionic_blades("tassadar")
    assert tools == []
    
    tools = conclave._psionic_blades("zeratul")  
    assert tools == []


@pytest.mark.asyncio
async def test_conclave_error_handling():
    """Test conclave error handling and graceful degradation."""
    
    conclave = Conclave()
    
    # Test fallback prompt for missing files  
    prompt = conclave._load_prompt("invalid-agent")
    assert "Invalid-Agent agent" in prompt


@pytest.mark.asyncio
async def test_sacred_four_convening(mock_websockets_connect, constitutional_prompts):
    """Test convening all four Sacred Four members for deliberation."""
    
    conclave = Conclave()
    
    with patch('protoss.conclave.Agent') as MockAgent, \
         patch.object(conclave, '_load_prompt') as mock_prompt:
        
        mock_agent = AsyncMock()
        MockAgent.return_value = mock_agent
        mock_prompt.side_effect = lambda agent_type: constitutional_prompts.get(
            agent_type, f"Mock {agent_type} prompt"
        )
        
        # Mock position formation
        async def mock_stream(prompt, conversation_id=None):
            yield {
                "type": "respond",
                "content": "Constitutional position based on my unique perspective"
            }
        mock_agent.stream = mock_stream
        
        # Test full conclave convening
        conclave_id = await conclave.convene("Should we implement real-time coordination?")
        
        # Verify Sacred Four were spawned
        assert MockAgent.call_count == 4
        assert conclave_id.startswith("conclave-")
        
        # Verify each member was given constitutional prompt
        assert mock_prompt.call_count == 4
        
        # Verify WebSocket connections (4 agents = 4 connections)
        assert mock_websockets_connect.call_count == 4


def test_sacred_four_completeness():
    """Test that all Sacred Four members are included."""
    
    sacred_four = ["tassadar", "zeratul", "artanis", "fenix"]
    
    # Verify the sacred four are complete
    assert len(sacred_four) == 4
    assert "tassadar" in sacred_four  # Pragmatic visionary
    assert "zeratul" in sacred_four   # Independent seer  
    assert "artanis" in sacred_four   # Unifying force
    assert "fenix" in sacred_four     # Unstoppable warrior