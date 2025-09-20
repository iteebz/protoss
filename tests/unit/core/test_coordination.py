"""Unit tests for coordination functions (flatten, parse)."""

from protoss.core.coordination import flatten, parse
from protoss.core.config import Config
from protoss.core.message import Message


def test_flatten_archon_sees_all_events():
    """Test that archon agent type sees full event stream."""
    messages = [
        Message("test", "agent1", "[THINK] Internal thinking"),
        Message("test", "agent1", "[CALL] Tool call"),
        Message("test", "agent1", "[RESULT] Tool result"),
        Message("test", "agent1", "Normal response"),
        Message("test", "agent2", "Another response"),
    ]

    config = Config(max_context=10)

    # Archon should see all events
    result = flatten(messages, config, agent_type="archon")

    assert "[THINK]" in result
    assert "[CALL]" in result
    assert "[RESULT]" in result
    assert "Normal response" in result
    assert "Another response" in result


def test_flatten_other_agents_see_filtered():
    """Test that non-archon agents see filtered event stream."""
    messages = [
        Message("test", "agent1", "[THINK] Internal thinking"),
        Message("test", "agent1", "[CALL] Tool call"),
        Message("test", "agent1", "[RESULT] Tool result"),
        Message("test", "agent1", "Normal response"),
        Message("test", "agent2", "Another response"),
    ]

    config = Config(max_context=10)

    # Zealot should see filtered events
    result = flatten(messages, config, agent_type="zealot")

    assert "[THINK]" not in result
    assert "[CALL]" not in result
    assert "[RESULT]" not in result
    assert "Normal response" in result
    assert "Another response" in result


def test_flatten_no_agent_type_defaults_to_filtered():
    """Test that no agent_type parameter defaults to filtered."""
    messages = [
        Message("test", "agent1", "[THINK] Internal thinking"),
        Message("test", "agent1", "Normal response"),
    ]

    config = Config(max_context=10)

    # Should default to filtered (non-archon behavior)
    result = flatten(messages, config)

    assert "[THINK]" not in result
    assert "Normal response" in result


def test_flatten_empty_messages():
    """Test flatten with empty message list."""
    config = Config(max_context=10)

    result = flatten([], config, agent_type="zealot")

    assert result == "You are the first agent working on this task."


def test_flatten_respects_max_context():
    """Test that flatten respects max_context limit."""
    messages = [Message("test", f"agent{i}", f"Message {i}") for i in range(20)]

    config = Config(max_context=5)

    result = flatten(messages, config, agent_type="zealot")

    # Should only contain last 5 messages
    assert "Message 15" in result
    assert "Message 19" in result
    assert "Message 10" not in result


def test_parse_despawn_signal():
    """Test parsing !despawn signal."""
    config = Config()

    signals = parse("Work complete. !despawn", config)

    assert signals.despawn is True
    assert signals.complete is False


def test_parse_complete_signal():
    """Test parsing [COMPLETE] signal."""
    config = Config(complete="[COMPLETE]")

    signals = parse("Task finished. [COMPLETE]", config)

    assert signals.complete is True
    assert signals.despawn is False


def test_parse_idle_signal_ignored():
    """[IDLE] markers are ignored in minimalist protocol."""
    config = Config()

    signals = parse("No work remaining. [IDLE]", config)

    assert signals.complete is False
    assert signals.despawn is False


def test_parse_multiple_signals():
    """Test parsing multiple signals in one response."""
    config = Config(complete="[COMPLETE]")

    signals = parse("Task done. !despawn [COMPLETE]", config)

    assert signals.complete is True
    assert signals.despawn is True


def test_parse_case_insensitive_despawn():
    """Test that !despawn parsing is case insensitive."""
    config = Config()

    signals_lower = parse("done !despawn", config)
    signals_upper = parse("done !DESPAWN", config)
    signals_mixed = parse("done !Despawn", config)

    assert signals_lower.despawn is True
    assert signals_upper.despawn is True
    assert signals_mixed.despawn is True


def test_parse_no_signals():
    """Test parsing response with no signals."""
    config = Config()

    signals = parse("Just a normal response", config)

    assert signals.complete is False
    assert signals.despawn is False
