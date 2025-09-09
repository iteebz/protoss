"""Tests for Carrier human-swarm coordination."""

import pytest
from unittest.mock import AsyncMock, patch
from protoss.units.carrier import Carrier, Interceptor


@pytest.fixture
def carrier():
    """Basic Carrier instance for testing."""
    return Carrier(carrier_id="carrier-test")


@pytest.fixture
def mock_constitutional_agents():
    """Mock Sacred Four agents for escalation testing."""
    return {
        "tassadar": AsyncMock(),
        "zeratul": AsyncMock(), 
        "artanis": AsyncMock(),
        "fenix": AsyncMock()
    }


class TestCarrierHumanInterface:
    """Test Carrier human command interface."""

    @pytest.mark.asyncio
    async def test_simple_execution_command(self, carrier):
        """Test basic execution command translation."""
        result = await carrier.interface_with_human("Execute task: build tokenizer")
        
        assert "COMMAND TRANSLATED TO SWARM" in result
        assert "build tokenizer" in result

    @pytest.mark.asyncio
    async def test_coordination_command(self, carrier):
        """Test swarm coordination via interceptors."""
        result = await carrier.interface_with_human("Coordinate all agents to run tests in parallel")
        
        assert "SWARM COORDINATION COMPLETE" in result
        assert "Interceptors deployed" in result
        assert "SUCCESS" in result

    @pytest.mark.asyncio
    async def test_constitutional_escalation(self, carrier):
        """Test escalation to Sacred Four for strategic decisions."""
        result = await carrier.interface_with_human("Should we refactor the architecture for better scaling?")
        
        assert "ESCALATED TO CONSTITUTIONAL COUNCIL" in result
        assert "Pending Sacred Four deliberation" in result
        assert "refactor the architecture" in result

    @pytest.mark.asyncio
    async def test_strategic_intent_parsing(self, carrier):
        """Test intent parsing accuracy."""
        # Test execution command
        intent = await carrier._parse_strategic_intent("Build tokenizer component")
        assert intent["requires_execution"] is True
        assert intent["requires_coordination"] is False
        assert intent["requires_deliberation"] is False

        # Test coordination command  
        intent = await carrier._parse_strategic_intent("Coordinate multiple agents for parallel testing")
        assert intent["requires_coordination"] is True
        assert intent["scope"] == "swarm"

        # Test constitutional command
        intent = await carrier._parse_strategic_intent("Should we change our architectural approach?")
        assert intent["requires_deliberation"] is True
        assert intent["uncertainty_level"] == "high"


class TestInterceptorCoordination:
    """Test Interceptor spawning and coordination."""

    @pytest.mark.asyncio
    async def test_interceptor_spawning(self, carrier):
        """Test spawning interceptors for coordination tasks."""
        interceptor_id = await carrier.spawn_interceptor(
            "Coordinate zealots for testing",
            "relay"
        )
        
        assert interceptor_id.startswith("interceptor-")
        assert len(carrier.active_interceptors) == 1
        assert carrier.active_interceptors[interceptor_id]["status"] == "active"

    @pytest.mark.asyncio
    async def test_coordination_task_decomposition(self, carrier):
        """Test decomposition of coordination tasks."""
        intent = {
            "command": "Run tests in parallel across all agents",
            "requires_coordination": True
        }
        
        tasks = carrier._decompose_coordination_task(intent)
        
        # Should create interceptor tasks
        assert len(tasks) >= 1
        assert "interceptor-1" in tasks
        assert "description" in tasks["interceptor-1"]

    @pytest.mark.asyncio 
    async def test_parallel_coordination_decomposition(self, carrier):
        """Test parallel coordination creates multiple interceptors."""
        intent = {
            "command": "Execute parallel testing across swarm",
            "requires_coordination": True
        }
        
        tasks = carrier._decompose_coordination_task(intent)
        
        # Should create multiple interceptors for parallel work
        assert len(tasks) == 2
        assert "interceptor-1" in tasks
        assert "interceptor-2" in tasks


class TestContextCompression:
    """Test context compression for human consumption."""

    @pytest.mark.asyncio
    async def test_successful_swarm_compression(self, carrier):
        """Test compression of successful swarm results."""
        swarm_results = {
            "interceptor-1": {
                "status": "completed",
                "agents_coordinated": 5,
                "summary": "Coordinated testing batch 1"
            },
            "interceptor-2": {
                "status": "completed", 
                "agents_coordinated": 3,
                "summary": "Coordinated testing batch 2"
            }
        }
        
        compressed = await carrier._compress_context_for_human(swarm_results)
        
        assert "SWARM COORDINATION COMPLETE" in compressed
        assert "Interceptors deployed: 2" in compressed
        assert "Agents coordinated: 8" in compressed
        assert "SUCCESS" in compressed

    @pytest.mark.asyncio
    async def test_partial_failure_compression(self, carrier):
        """Test compression handles partial failures."""
        swarm_results = {
            "interceptor-1": {
                "status": "completed",
                "agents_coordinated": 5,
                "summary": "Success"
            },
            "interceptor-2": {
                "status": "failed",
                "agents_coordinated": 0,
                "summary": "Failed coordination"
            }
        }
        
        compressed = await carrier._compress_context_for_human(swarm_results)
        
        assert "Tasks completed: 1/2" in compressed
        assert "PARTIAL" in compressed


class TestCarrierStatus:
    """Test Carrier status and health monitoring."""

    @pytest.mark.asyncio
    async def test_swarm_health_monitoring(self, carrier):
        """Test swarm health monitoring."""
        health = await carrier.monitor_swarm_health()
        
        assert "active_interceptors" in health
        assert "context_buffer_size" in health
        assert "coordination_capacity" in health
        assert health["coordination_capacity"] == "optimal"

    def test_coordination_summary(self, carrier):
        """Test human-readable coordination status."""
        # Add some interceptors
        carrier.active_interceptors["test-1"] = {"status": "active"}
        carrier.context_buffer.append({"test": "data"})
        
        summary = carrier.get_coordination_summary()
        
        assert "CARRIER STATUS" in summary
        assert "Active Interceptors: 1" in summary
        assert "Context Buffer: 1 items" in summary
        assert "OPTIMAL" in summary

    def test_high_load_detection(self, carrier):
        """Test high load detection in status."""
        # Simulate high interceptor load
        for i in range(12):
            carrier.active_interceptors[f"test-{i}"] = {"status": "active"}
        
        summary = carrier.get_coordination_summary()
        assert "HIGH_LOAD" in summary


class TestInterceptorAgents:
    """Test Interceptor agent functionality."""

    def test_interceptor_creation(self):
        """Test Interceptor creation."""
        interceptor = Interceptor("interceptor-test", "carrier-parent")
        
        assert interceptor.id == "interceptor-test"
        assert interceptor.parent_carrier == "carrier-parent"
        assert interceptor.coordination_task is None
        assert interceptor.target_agents == []

    @pytest.mark.asyncio
    async def test_agent_coordination(self):
        """Test Interceptor agent coordination."""
        interceptor = Interceptor("interceptor-test", "carrier-parent")
        
        agents = ["zealot-1", "zealot-2", "zealot-3"]
        results = await interceptor.coordinate_agents(agents, "run tests")
        
        assert len(results) == 3
        assert "zealot-1" in results
        assert "run tests" in results["zealot-1"]

    @pytest.mark.asyncio
    async def test_status_gathering(self):
        """Test Interceptor status gathering."""
        interceptor = Interceptor("interceptor-test", "carrier-parent")
        
        agents = ["zealot-1", "zealot-2"]
        status = await interceptor.gather_status(agents)
        
        assert len(status) == 2
        assert "zealot-1" in status
        assert status["zealot-1"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_interceptor_despawn(self):
        """Test Interceptor despawning."""
        interceptor = Interceptor("interceptor-test", "carrier-parent")
        
        summary = await interceptor.despawn()
        
        assert "interceptor-test" in summary
        assert "coordination complete" in summary


class TestCarrierConstitutionalFramework:
    """Test Carrier constitutional identity and resistance."""

    def test_constitutional_identity_exists(self, carrier):
        """Test Carrier has constitutional identity."""
        assert hasattr(carrier, 'identity')
        assert "emissary, not a diplomat" in carrier.identity
        assert "RESIST BULLSHIT" in carrier.identity

    @pytest.mark.asyncio
    async def test_escalation_format(self, carrier):
        """Test constitutional escalation maintains proper format."""
        intent = {
            "command": "Should we pivot architecture?",
            "uncertainty_level": "high"
        }
        
        result = await carrier._escalate_to_constitutional(intent)
        
        # Verify escalation format
        assert "ESCALATED TO CONSTITUTIONAL COUNCIL" in result
        assert "Decision required:" in result
        assert "pivot architecture" in result
        assert "constitutional guidance" in result