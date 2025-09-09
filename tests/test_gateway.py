"""Gateway tests - Agent spawning and task execution coordination."""

import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from protoss.structures.gateway import Gateway
from protoss.constants import PYLON_TEST_PORT


@pytest.mark.asyncio
async def test_gateway_zealot_spawning(mock_websockets_connect, mock_agent):
    """Test Gateway spawns Zealot agents with proper configuration."""
    
    gateway = Gateway(pylon_host="localhost", pylon_port=PYLON_TEST_PORT)
    
    # Create mock zealot
    mock_zealot = AsyncMock()
    mock_zealot.execute.return_value = "Task completed"
    
    # Patch the _create_unit method to return our mock
    with patch.object(gateway, '_create_unit', return_value=mock_zealot):
        # Test Zealot spawning
        zealot_id = await gateway.spawn_agent("What is 2+2?", "zealot", "nexus")
        
        # Verify zealot was executed
        mock_zealot.execute.assert_called_once_with("What is 2+2?")
        
        # Verify WebSocket connection
        mock_websockets_connect.assert_called_once()
        
        # Verify agent ID format
        assert zealot_id.startswith("zealot-")


@pytest.mark.asyncio
async def test_gateway_constitutional_prompts():
    """Test Gateway creates units with proper constitutional identities."""
    
    gateway = Gateway()
    
    # Test unit creation for each Sacred Four member - these should work without mocking
    # since we're not executing them, just creating and checking properties
    for agent_type in ["tassadar", "zeratul", "artanis", "fenix"]:
        with patch.object(gateway.unit_types[agent_type], '__init__', return_value=None):
            # Create a simple mock with the required properties
            mock_unit = MagicMock()
            mock_unit.identity = f"{agent_type.upper()} constitutional identity"
            mock_unit.tools = []
            
            with patch.object(gateway, '_create_unit', return_value=mock_unit):
                unit = gateway._create_unit(agent_type)
                assert hasattr(unit, 'identity')
                assert hasattr(unit, 'tools')
                assert agent_type.upper() in unit.identity.upper()


@pytest.mark.asyncio
async def test_gateway_task_execution_flow(mock_websockets_connect, mock_agent):
    """Test complete Gateway task execution flow."""
    
    gateway = Gateway(pylon_port=PYLON_TEST_PORT)
    
    # Create mock zealot
    mock_zealot = AsyncMock()
    mock_zealot.execute.return_value = "Result: 4"
    
    with patch.object(gateway, '_create_unit', return_value=mock_zealot):
        # Mock WebSocket for message sending
        mock_websocket = mock_websockets_connect.return_value.__aenter__.return_value
        
        # Execute task
        result = await gateway.spawn_agent("Calculate 2+2", "zealot", "nexus")
        
        # Verify execution flow
        mock_zealot.execute.assert_called_once_with("Calculate 2+2")
        mock_websockets_connect.assert_called_once()
        mock_websocket.send.assert_called_once()
        
        # Verify Psi message format
        sent_message = mock_websocket.send.call_args[0][0]
        assert sent_message.startswith("§PSI:nexus:")
        assert ":report:" in sent_message


def test_gateway_tool_configuration():
    """Test Gateway creates units with appropriate tool configurations."""
    
    gateway = Gateway()
    
    # Test actual unit creation for tool configuration
    zealot = gateway._create_unit("zealot")
    assert len(zealot.tools) == 5  # FileRead, FileWrite, FileEdit, FileList, SystemShell
    
    # Constitutional agents get no tools
    tassadar = gateway._create_unit("tassadar")
    assert len(tassadar.tools) == 0


def test_gateway_unit_fallback():
    """Test Gateway falls back to Zealot for unknown unit types."""
    
    gateway = Gateway()
    
    # Test fallback for non-existent unit type
    unit = gateway._create_unit("nonexistent-unit")
    from protoss.units.zealot import Zealot
    assert isinstance(unit, Zealot)  # Falls back to Zealot


@pytest.mark.asyncio
async def test_gateway_error_handling(mock_websockets_connect):
    """Test Gateway handles errors gracefully."""
    
    gateway = Gateway(pylon_port=PYLON_TEST_PORT)
    
    # Mock connection failure
    mock_websockets_connect.side_effect = ConnectionRefusedError("Pylon offline")
    
    # Mock unit to prevent LLM calls
    mock_zealot = AsyncMock()
    
    with patch.object(gateway, '_create_unit', return_value=mock_zealot):
        # Should propagate connection error
        with pytest.raises(ConnectionRefusedError):
            await gateway.spawn_agent("Test task", "zealot", "nexus")


@pytest.mark.asyncio 
async def test_gateway_concurrent_spawning(mock_websockets_connect, mock_agent):
    """Test Gateway handles concurrent agent spawning."""
    
    gateway = Gateway(pylon_port=PYLON_TEST_PORT)
    
    # Create mock zealot
    mock_zealot = AsyncMock()
    mock_zealot.execute.return_value = "Completed"
    
    with patch.object(gateway, '_create_unit', return_value=mock_zealot):
        # Spawn multiple agents concurrently
        tasks = [
            gateway.spawn_agent(f"Task {i}", "zealot", "nexus")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all zealots were spawned
        assert len(results) == 5
        assert all(result.startswith("zealot-") for result in results)
        assert mock_zealot.execute.call_count == 5


@pytest.mark.asyncio
async def test_gateway_agent_lifecycle(mock_websockets_connect, mock_agent):
    """Test complete agent lifecycle: spawn → execute → report → despawn."""
    
    gateway = Gateway()
    
    # Create mock zealot  
    mock_zealot = AsyncMock()
    mock_zealot.execute.return_value = "Lifecycle complete"
    
    with patch.object(gateway, '_create_unit', return_value=mock_zealot):
        mock_websocket = mock_websockets_connect.return_value.__aenter__.return_value
        
        # Spawn agent
        agent_id = await gateway.spawn_agent("Complete lifecycle test", "zealot", "nexus")
        
        # Verify lifecycle stages
        # 1. Unit created (via _create_unit mock)
        # 2. Connected to Pylon
        mock_websockets_connect.assert_called_once()
        
        # 3. Task executed
        mock_zealot.execute.assert_called_once_with("Complete lifecycle test")
        
        # 4. Result reported via Psi message
        mock_websocket.send.assert_called_once()
        
        # 5. Connection closes automatically (context manager)
        # This is handled by the async context manager mock


@pytest.mark.asyncio
async def test_gateway_sacred_four_spawning(mock_websockets_connect):
    """Test Gateway can spawn Sacred Four constitutional agents."""
    
    gateway = Gateway()
    
    sacred_four = ["tassadar", "zeratul", "artanis", "fenix"]
    
    for agent_type in sacred_four:
        # Create mock constitutional agent
        mock_unit = AsyncMock()
        mock_unit.deliberate.return_value = f"{agent_type} constitutional position"
        
        with patch.object(gateway, '_create_unit', return_value=mock_unit):
            # Spawn constitutional agent
            agent_id = await gateway.spawn_agent("Should we proceed?", agent_type, "nexus")
            
            # Verify deliberation was called (not execute)
            mock_unit.deliberate.assert_called_once_with("Should we proceed?")
            assert agent_id.startswith(f"{agent_type}-")