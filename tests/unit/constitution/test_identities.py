"""Tests for constitutional identities and their principles."""

from src.protoss.constitution import (
    CONSTITUTIONS,
    COMPLETION_SIGNAL,
    EXIT_SIGNALS,
    DEFAULT_AGENTS,
)


def test_default_agents_defined():
    """DEFAULT_AGENTS is single source of truth for agent types."""
    assert DEFAULT_AGENTS == ["zealot", "sentinel", "harbinger"]
    assert len(DEFAULT_AGENTS) == 3


def test_all_default_agents_have_constitution():
    """Each agent in DEFAULT_AGENTS has a defined constitutional identity."""
    for agent in DEFAULT_AGENTS:
        assert agent in CONSTITUTIONS, f"{agent} missing from CONSTITUTIONS"
        assert isinstance(CONSTITUTIONS[agent], str), f"{agent} identity not a string"
        assert len(CONSTITUTIONS[agent]) > 0, f"{agent} identity is empty"


def test_zealot_identity_defines_core_mandate():
    """Zealot constitution specifies core mandate of skeptical questioning."""
    zealot = CONSTITUTIONS["zealot"]

    assert "ZEALOT" in zealot.upper(), "Zealot should identify as ZEALOT"
    assert "complexity" in zealot.lower(), "Zealot should critique complexity"
    assert "simplicity" in zealot.lower(), "Zealot should advocate simplicity"
    assert (
        "push back" in zealot.lower() or "refuse" in zealot.lower()
    ), "Zealot should refuse bad ideas"


def test_sentinel_identity_anchors_reality():
    """Sentinel constitution specifies reality-grounding mandate."""
    sentinel = CONSTITUTIONS["sentinel"]

    assert "SENTINEL" in sentinel.upper(), "Sentinel should identify as SENTINEL"
    assert "truth" in sentinel.lower(), "Sentinel should anchor in truth"
    assert "reality" in sentinel.lower(), "Sentinel should ground in reality"
    assert "question" in sentinel.lower(), "Sentinel should question assertions"


def test_harbinger_identity_creates_clarity():
    """Harbinger constitution specifies clarity-through-tension mandate."""
    harbinger = CONSTITUTIONS["harbinger"]

    assert "HARBINGER" in harbinger.upper(), "Harbinger should identify as HARBINGER"
    assert "clarity" in harbinger.lower(), "Harbinger should forge clarity"
    assert "tension" in harbinger.lower(), "Harbinger should use productive tension"
    assert (
        "simplest" in harbinger.lower() or "simple" in harbinger.lower()
    ), "Harbinger should reframe to simplest solution"


def test_exit_signals_defined():
    """EXIT_SIGNALS is authoritative list of agent termination signals."""
    assert EXIT_SIGNALS == {"!done", "!consensus", "!complete", "!despawn"}
    assert len(EXIT_SIGNALS) == 4


def test_completion_signal_is_single_source():
    """COMPLETION_SIGNAL is single source for task completion."""
    assert COMPLETION_SIGNAL == "!complete"
    assert (
        COMPLETION_SIGNAL in EXIT_SIGNALS
    ), "Completion signal should be in exit signals"


def test_constitutional_principles():
    """Constitutions guide behavior through identity, not explicit commands."""
    for agent, identity in CONSTITUTIONS.items():
        # Should define identity/mandate
        assert any(
            word in identity.lower() for word in ["you are", "mandate", "principles"]
        ), f"{agent} should state identity"

        # Should NOT be a task list
        assert not identity.lower().startswith(
            "1."
        ), f"{agent} should not be numbered tasks"
        assert "step 1" not in identity.lower(), f"{agent} should not prescribe steps"


def test_constitutions_are_not_empty():
    """Each constitution has substantive content."""
    for agent, identity in CONSTITUTIONS.items():
        lines = [line.strip() for line in identity.split("\n") if line.strip()]
        assert len(lines) > 3, f"{agent} constitution too brief"


def test_agent_types_consistent_across_exports():
    """Agent types in DEFAULT_AGENTS match constitution keys."""
    constitution_agents = set(CONSTITUTIONS.keys())
    default_agents = set(DEFAULT_AGENTS)

    assert (
        default_agents == constitution_agents
    ), f"Agent type mismatch: {default_agents} vs {constitution_agents}"
