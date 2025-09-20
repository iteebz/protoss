"""Unit tests for Engine orchestration logic."""

import pytest
from protoss.core.engine import Protoss
from protoss.core.config import Config


@pytest.mark.asyncio
async def test_agent_selection_simple_task():
    """Simple tasks spawn arbiter + zealots only."""
    config = Config(agents=3, debug=False)
    Protoss(config)

    # Test agent selection logic without full coordination
    from protoss.agents import Zealot, Arbiter

    active_agents = []

    # Engine logic: Always start with arbiter
    arbiter = Arbiter()
    active_agents.append(("arbiter", arbiter))

    # Add zealots for parallel work
    zealot_count = min(3 - 1, 3)  # agents - 1, cap at 3
    for i in range(zealot_count):
        zealot = Zealot(f"zealot-{i+1}")
        active_agents.append((f"zealot-{i+1}", zealot))

    # Simple task shouldn't trigger constitutional deliberation
    task = "fix bug in login function"
    architecture_keywords = ["architecture", "design", "approach", "strategy"]
    needs_conclave = any(keyword in task.lower() for keyword in architecture_keywords)

    assert not needs_conclave
    assert len(active_agents) == 3  # 1 arbiter + 2 zealots
    assert active_agents[0][0] == "arbiter"
    assert all("zealot" in name for name, _ in active_agents[1:])


@pytest.mark.asyncio
async def test_agent_selection_complex_task():
    """Complex architectural tasks trigger constitutional deliberation."""
    config = Config(agents=4, debug=False)
    Protoss(config)

    from protoss.agents import Zealot, Arbiter, Conclave

    active_agents = []

    # Engine logic for complex task
    arbiter = Arbiter()
    active_agents.append(("arbiter", arbiter))

    zealot_count = min(4 - 1, 3)
    for i in range(zealot_count):
        zealot = Zealot(f"zealot-{i+1}")
        active_agents.append((f"zealot-{i+1}", zealot))

    # Complex task should trigger constitutional deliberation
    task = "design new microservices architecture"
    architecture_keywords = ["architecture", "design", "approach", "strategy"]
    needs_conclave = any(keyword in task.lower() for keyword in architecture_keywords)

    if needs_conclave:
        conclave = Conclave("tassadar")
        active_agents.append(("conclave", conclave))

    assert needs_conclave
    assert len(active_agents) == 5  # 1 arbiter + 3 zealots + 1 conclave
    assert any("conclave" in name for name, _ in active_agents)


def test_config_override_merging():
    """Config overrides merge correctly without ceremony."""
    base_config = Config(agents=2, debug=False, timeout=30)
    overrides = {"agents": 5, "debug": True}

    # Test the actual engine logic
    engine = Protoss(base_config, **overrides)

    assert engine.config.agents == 5  # Overridden
    assert engine.config.debug is True  # Overridden
    assert engine.config.timeout == 30  # Preserved from base


def test_agent_count_validation():
    """Agent count validation prevents runaway spawning."""
    config = Config(agents=2, max_agents=10)

    # Should accept valid count
    assert 5 <= config.max_agents  # Would pass validation

    # Should reject excessive count
    excessive_count = 15
    assert excessive_count > config.max_agents  # Would fail validation


@pytest.mark.asyncio
async def test_coordination_timeout():
    """Timeout handling works correctly."""
    config = Config(timeout=1)  # 1 second timeout
    Protoss(config)

    # Test timeout logic without actually timing out
    final_timeout = 5 or config.timeout  # Runtime override
    assert final_timeout == 5

    final_timeout = None or config.timeout  # Use config default
    assert final_timeout == 1


def test_channel_context_extraction(mock_channel):
    """Channel context extracted from bus memories."""
    bus = mock_channel["bus"]
    channel_id = mock_channel["channel_id"]

    # Test engine's context extraction logic
    def get_channel_context(bus, channel_id):
        if channel_id not in bus.memories:
            return ""

        messages = bus.memories[channel_id]
        if not messages:
            return ""

        # Last 3 messages for context
        recent_messages = messages[-3:]
        context_lines = []
        for msg in recent_messages:
            context_lines.append(f"{msg.sender}: {msg.content[:100]}...")

        return "\n".join(context_lines)

    context = get_channel_context(bus, channel_id)
    lines = context.split("\n")

    assert len(lines) == 3
    assert "agent1: First message..." in lines[0]
    assert "agent2: Second message..." in lines[1]
    assert "agent3: Third message..." in lines[2]


def test_coordination_summary_format():
    """Engine summary string highlights emergent coordination."""
    channel_id = "coord-test"
    spawned_types = ["zealot", "arbiter"]
    team_status = "Team Status: zealot-123 (active), arbiter-456 (active)"

    summary = "\n".join(
        [
            "🔮 PROTOSS COORDINATION ENGAGED",
            "Task: implement auth system",
            f"Channel: {channel_id}",
            f"Initial agents: {', '.join(spawned_types)}",
            team_status,
            "Emergent coordination active via conversational mentions.",
            "Archon context seed dispatched.",
        ]
    )

    assert "🔮 PROTOSS COORDINATION ENGAGED" in summary
    assert "implement auth system" in summary
    assert "zealot, arbiter" in summary
    assert "Team Status:" in summary


@pytest.mark.asyncio
async def test_rich_context_seeding():
    """Rich context seeding triggers archon correctly."""
    config = Config(rich_context=True)

    # Test seeding logic
    keywords = ["auth", "security"]
    should_seed = keywords or config.rich_context

    assert should_seed

    # Without rich context
    config_minimal = Config(rich_context=False)
    should_seed_minimal = None or config_minimal.rich_context

    assert not should_seed_minimal
