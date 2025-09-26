"""Reference-grade unit tests for the parser module."""

import pytest
from protoss.core.parser import signals
from protoss.core.protocols import Mention, Despawn, Emergency


def test_empty_string():
    """Empty string yields no signals."""
    assert signals("") == []


def test_whitespace_string():
    """Whitespace string yields no signals."""
    assert signals("   \n\t  ") == []


def test_no_signals():
    """Content with no mentions or guardrails returns empty list."""
    content = "This is a regular message without any special commands."
    assert signals(content) == []


@pytest.mark.parametrize(
    "content, expected_mentions",
    [
        # Valid mentions
        ("Hello @archon, please review this.", [Mention(agent_name="archon")]),
        (
            "@zealot and @arbiter, coordinate.",
            [Mention(agent_name="zealot"), Mention(agent_name="arbiter")],
        ),
        ("Hey @ArBiTeR, what's up?", [Mention(agent_name="arbiter")]),
        (
            "(@oracle) - check this. @zealot! Done.",
            [Mention(agent_name="oracle"), Mention(agent_name="zealot")],
        ),
        ("Hello @archon. Please review.", [Mention(agent_name="archon")]),
        ("Is this for @zealot?", [Mention(agent_name="zealot")]),
        ("Call @arbiter!", [Mention(agent_name="arbiter")]),
        # Invalid mentions (false positives)
        (
            "email@example.com, #hashtag, but @real_agent.",
            [],  # 'real_agent' is not a discovered agent
        ),
        ("This is not an @email.com.", []),
        ("Another @test-agent (hyphen not allowed by regex).", []),
        ("This is a regular message without any special commands or @symbols.", []),
    ],
    ids=[
        "valid_archon",
        "valid_zealot_arbiter",
        "valid_arbiter_case_insensitive",
        "valid_oracle_zealot_punctuation",
        "valid_archon_period",
        "valid_zealot_question",
        "valid_arbiter_exclamation",
        "invalid_email_hashtag",
        "invalid_email_domain",
        "invalid_hyphenated_agent",
        "no_mentions",
    ],
)
def test_mentions_valid(content, expected_mentions):
    """@mentions are parsed correctly across various valid and invalid scenarios."""
    result = [s for s in signals(content) if isinstance(s, Mention)]
    # Sort results for deterministic comparison, as regex match order is not guaranteed
    result.sort(key=lambda x: x.agent_name)
    expected_mentions.sort(key=lambda x: x.agent_name)
    assert result == expected_mentions


@pytest.mark.parametrize(
    "content, expected_despawn, expected_emergency",
    [
        # Basic guardrails
        ("Task complete !despawn.", True, False),
        ("System critical !emergency.", False, True),
        # Multiple guardrails
        ("All done !despawn. System failure !emergency.", True, True),
        # Case-insensitivity
        ("Task complete !DeSpAwN. System critical !EmErGeNcY.", True, True),
        ("I need to !DeSpAwN now. This is an !EmErGeNcY.", True, True),
        # Guardrails embedded in text
        ("Please !despawn now.", True, False),
        ("This is an !emergency situation.", False, True),
        # No guardrails
        ("This is a normal message.", False, False),
        ("What about despawn?", False, False),
        ("Is this an emergency?", False, False),
    ],
    ids=[
        "despawn_basic",
        "emergency_basic",
        "both_basic",
        "both_case_insensitive",
        "both_embedded_case_insensitive",
        "despawn_embedded",
        "emergency_embedded",
        "no_guardrails_normal",
        "no_guardrails_word_despawn",
        "no_guardrails_word_emergency",
    ],
)
def test_guardrails_valid(content, expected_despawn, expected_emergency):
    """!despawn and !emergency guardrails are parsed correctly."""
    result = signals(content)
    assert (Despawn() in result) == expected_despawn
    assert (Emergency() in result) == expected_emergency


def test_mixed_signals():
    """Content containing both @mentions and guardrails."""
    content = "Hello @archon, please review this !despawn. This is an !emergency."
    expected = [
        Mention(agent_name="archon"),
        Despawn(),
        Emergency(),
    ]
    result = signals(content)
    # Sort mentions for deterministic comparison
    mentions_in_result = [s for s in result if isinstance(s, Mention)]
    mentions_in_result.sort(key=lambda x: x.agent_name)

    guardrails_in_result = [s for s in result if not isinstance(s, Mention)]

    mentions_in_expected = [s for s in expected if isinstance(s, Mention)]
    mentions_in_expected.sort(key=lambda x: x.agent_name)

    guardrails_in_expected = [s for s in expected if not isinstance(s, Mention)]

    assert mentions_in_result == mentions_in_expected
    assert guardrails_in_result == guardrails_in_expected
