"""Unit tests for Gateway spawning contracts.

Fast, isolated tests validating Gateway behavior without infrastructure dependencies.
Uses mocking for deterministic agent responses and Khala communication.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from protoss.structures.gateway import Gateway


class TestGatewaySpawning:
    """Test Gateway unit spawning and coordination contracts."""

    def test_gateway_initialization(self):
        """Test Gateway initializes with correct unit types."""
        gateway = Gateway()

        # Verify unit type registry
        expected_types = {"zealot", "archon", "tassadar", "zeratul", "artanis", "fenix"}
        assert set(gateway.unit_types.keys()) == expected_types

    def test_spawn_default_zealot(self):
        """Test spawning default zealot unit."""
        gateway = Gateway()

        with patch("protoss.structures.gateway.Agent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            unit = gateway.spawn("zealot")

            # Verify unit creation
            assert unit is not None
            assert hasattr(unit, "agent")
            assert unit.agent == mock_agent

            # Verify agent configured with unit identity and tools
            mock_agent_class.assert_called_once()
            call_kwargs = mock_agent_class.call_args.kwargs
            assert "instructions" in call_kwargs
            assert "tools" in call_kwargs

    def test_spawn_constitutional_units(self):
        """Test spawning Sacred Four constitutional units."""
        gateway = Gateway()
        constitutional_types = ["tassadar", "zeratul", "artanis", "fenix"]

        for unit_type in constitutional_types:
            with patch("protoss.structures.gateway.Agent") as mock_agent_class:
                mock_agent = Mock()
                mock_agent_class.return_value = mock_agent

                unit = gateway.spawn(unit_type)

                assert unit is not None
                assert hasattr(unit, "agent")
                # Each constitutional unit should have distinct identity
                assert mock_agent_class.called

    def test_spawn_with_custom_id(self):
        """Test spawning with custom unit ID."""
        gateway = Gateway()
        custom_id = "custom-zealot-123"

        with patch("protoss.structures.gateway.Agent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            unit = gateway.spawn("zealot", custom_id)

            # Should create unit with custom ID
            assert unit is not None
            assert hasattr(unit, "agent")


class TestGatewayWarp:
    """Test Gateway natural coordination warp functionality."""

    @pytest.mark.asyncio
    async def test_basic_warp_defaults(self):
        """Test basic warp with default parameters."""
        gateway = Gateway()

        with patch.object(gateway, "spawn") as mock_spawn:
            # Mock unit that returns immediately
            mock_unit = Mock()
            mock_unit.execute = AsyncMock(return_value="Task complete")
            mock_spawn.return_value = mock_unit

            result = await gateway.warp("test task")

            # Should create squad ID
            assert result.startswith("Squad squad-")
            assert "completed coordination" in result

            # Should spawn default 3 zealots
            assert mock_spawn.call_count == 3

            # All spawns should be zealots by default
            for call in mock_spawn.call_args_list:
                assert call[0][0] == "zealot"

    @pytest.mark.asyncio
    async def test_warp_custom_agent_count(self):
        """Test warp with custom agent count."""
        gateway = Gateway()

        with patch.object(gateway, "spawn") as mock_spawn:
            mock_unit = Mock()
            mock_unit.execute = AsyncMock(return_value="Task complete")
            mock_spawn.return_value = mock_unit

            result = await gateway.warp("test task", agent_count=5)

            # Should spawn 5 agents
            assert mock_spawn.call_count == 5
            assert "5/5 successful agents" in result

    @pytest.mark.asyncio
    async def test_warp_constitutional_unit_types(self):
        """Test warp with constitutional unit types."""
        gateway = Gateway()
        unit_types = ["tassadar", "zeratul", "artanis", "fenix"]

        with patch.object(gateway, "spawn") as mock_spawn:
            mock_unit = Mock()
            mock_unit.execute = AsyncMock(return_value="Constitutional position")
            mock_spawn.return_value = mock_unit

            await gateway.warp(
                "strategic question", agent_count=4, unit_types=unit_types
            )

            # Should spawn 4 constitutional units
            assert mock_spawn.call_count == 4

            # Verify correct unit types spawned
            spawned_types = [call[0][0] for call in mock_spawn.call_args_list]
            assert spawned_types == unit_types

    @pytest.mark.asyncio
    async def test_warp_custom_pathway_id(self):
        """Test warp with custom pathway ID."""
        gateway = Gateway()
        custom_pathway = "custom-conclave-123"

        with patch.object(gateway, "spawn") as mock_spawn:
            mock_unit = Mock()
            mock_unit.execute = AsyncMock(return_value="Complete")
            mock_spawn.return_value = mock_unit

            result = await gateway.warp("test task", pathway_id=custom_pathway)

            # Should use custom pathway ID
            assert custom_pathway in result

    @pytest.mark.asyncio
    async def test_warp_handles_agent_failures(self):
        """Test warp gracefully handles agent execution failures."""
        gateway = Gateway()

        with patch.object(gateway, "spawn") as mock_spawn:
            # First agent succeeds, second fails, third succeeds
            mock_units = []
            for i in range(3):
                mock_unit = Mock()
                if i == 1:  # Second agent fails
                    mock_unit.execute = AsyncMock(side_effect=Exception("Agent failed"))
                else:
                    mock_unit.execute = AsyncMock(return_value="Success")
                mock_units.append(mock_unit)

            mock_spawn.side_effect = mock_units

            result = await gateway.warp("test task", agent_count=3)

            # Should report partial success
            assert "2/3 successful agents" in result

    @pytest.mark.asyncio
    async def test_warp_coordination_task_format(self):
        """Test warp formats coordination task correctly."""
        gateway = Gateway()
        test_task = "build authentication system"

        with patch.object(gateway, "spawn") as mock_spawn:
            mock_unit = Mock()
            # Capture the task passed to execute
            executed_tasks = []

            async def capture_execute(task, pathway):
                executed_tasks.append(task)
                return "Complete"

            mock_unit.execute = capture_execute
            mock_spawn.return_value = mock_unit

            await gateway.warp(test_task, agent_count=2)

            # Should format coordination task for each agent
            assert len(executed_tasks) == 2

            for i, task in enumerate(executed_tasks):
                assert "COORDINATION TASK:" in task
                assert test_task in task
                assert f"agent {i+1} of 2" in task
                assert "constitutional identity" in task
