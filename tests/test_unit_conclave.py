"""Unit tests for Conclave constitutional deliberation contracts.

Fast, isolated tests validating Conclave behavior without infrastructure dependencies.
Tests position-first deliberation pattern and Gateway integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from protoss.conclave import Conclave


class TestConclaveInitialization:
    """Test Conclave initialization and configuration."""

    def test_conclave_initialization(self):
        """Test Conclave initializes with Gateway dependency."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()

            assert conclave.gateway == mock_gateway
            mock_gateway_class.assert_called_once()

    def test_sacred_four_types_defined(self):
        """Test Conclave uses Sacred Four constitutional types."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.warp = AsyncMock(return_value="result")
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()

            # Test that convene uses Sacred Four types
            asyncio.run(conclave.convene("test question"))

            # Verify warp called with Sacred Four types
            call_kwargs = mock_gateway.warp.call_args.kwargs
            expected_types = ["tassadar", "zeratul", "artanis", "fenix"]
            assert call_kwargs["unit_types"] == expected_types


class TestConclaveConvene:
    """Test Conclave constitutional deliberation convening."""

    @pytest.mark.asyncio
    async def test_convene_creates_conclave_id(self):
        """Test convene generates unique conclave ID."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.warp = AsyncMock(return_value="conclave-result")
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()
            result = await conclave.convene("Test question")

            # Should return result from Gateway.warp
            assert result == "conclave-result"

    @pytest.mark.asyncio
    async def test_convene_calls_gateway_warp_correctly(self):
        """Test convene calls Gateway.warp with correct parameters."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.warp = AsyncMock(return_value="squad-123")
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()
            question = "Should we use microservices?"

            await conclave.convene(question)

            # Verify Gateway.warp called with constitutional parameters
            mock_gateway.warp.assert_called_once()
            call_args = mock_gateway.warp.call_args

            # Check task content
            task_arg = call_args[0][0]  # First positional argument
            assert "CONSTITUTIONAL DELIBERATION:" in task_arg
            assert question in task_arg
            assert "position independently" in task_arg

            # Check keyword arguments
            call_kwargs = call_args.kwargs
            assert call_kwargs["agent_count"] == 4
            assert call_kwargs["unit_types"] == [
                "tassadar",
                "zeratul",
                "artanis",
                "fenix",
            ]
            assert call_kwargs["pathway_id"].startswith("conclave-")

    @pytest.mark.asyncio
    async def test_convene_unique_pathway_ids(self):
        """Test convene generates unique pathway IDs for concurrent deliberations."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.warp = AsyncMock(return_value="result")
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()

            # Run multiple concurrent convenes
            tasks = [
                conclave.convene("Question 1"),
                conclave.convene("Question 2"),
                conclave.convene("Question 3"),
            ]

            await asyncio.gather(*tasks)

            # Should have 3 warp calls with unique pathway IDs
            assert mock_gateway.warp.call_count == 3

            pathway_ids = []
            for call in mock_gateway.warp.call_args_list:
                pathway_id = call.kwargs["pathway_id"]
                pathway_ids.append(pathway_id)
                assert pathway_id.startswith("conclave-")

            # All pathway IDs should be unique
            assert len(set(pathway_ids)) == 3

    @pytest.mark.asyncio
    async def test_convene_handles_gateway_errors(self):
        """Test convene propagates Gateway errors appropriately."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.warp = AsyncMock(side_effect=Exception("Gateway failed"))
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()

            # Should propagate Gateway errors
            with pytest.raises(Exception, match="Gateway failed"):
                await conclave.convene("Test question")

    @pytest.mark.asyncio
    async def test_convene_position_first_instruction(self):
        """Test convene includes position-first deliberation instruction."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.warp = AsyncMock(return_value="result")
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()
            await conclave.convene("Strategic question")

            # Check the task instruction format
            call_args = mock_gateway.warp.call_args
            task_instruction = call_args[0][0]

            # Should implement position-first pattern
            assert (
                "First: Each agent establishes your constitutional position independently"
                in task_instruction
            )
            assert "Then coordinate via PSI to reach consensus" in task_instruction

    @pytest.mark.asyncio
    async def test_convene_constitutional_diversity_instruction(self):
        """Test convene instructs agents to use constitutional perspectives."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.warp = AsyncMock(return_value="result")
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()
            await conclave.convene("Technical decision")

            call_args = mock_gateway.warp.call_args
            task_instruction = call_args[0][0]

            # Should reference constitutional diversity
            assert "constitutional position" in task_instruction.lower()

            # Should instruct natural coordination
            assert "coordinate via PSI" in task_instruction


class TestConclaveEdgeCases:
    """Test Conclave edge case handling."""

    @pytest.mark.asyncio
    async def test_convene_empty_question(self):
        """Test convene handles empty question gracefully."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.warp = AsyncMock(return_value="result")
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()

            # Should handle empty question without crashing
            result = await conclave.convene("")
            assert result is not None

            # Should still call Gateway with proper structure
            mock_gateway.warp.assert_called_once()

    @pytest.mark.asyncio
    async def test_convene_very_long_question(self):
        """Test convene handles very long questions."""
        with patch("protoss.structures.gateway.Gateway") as mock_gateway_class:
            mock_gateway = Mock()
            mock_gateway.warp = AsyncMock(return_value="result")
            mock_gateway_class.return_value = mock_gateway

            conclave = Conclave()
            long_question = "Should we " + "implement " * 1000 + "this solution?"

            # Should handle long question without issues
            result = await conclave.convene(long_question)
            assert result is not None

            # Question should be included in task
            call_args = mock_gateway.warp.call_args
            task_instruction = call_args[0][0]
            assert long_question in task_instruction
