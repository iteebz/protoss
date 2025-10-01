"""Unit tests for message routing."""

from src.protoss.lib.routing import parse_route, format_stub


def test_parse_route_prefix():
    target, body = parse_route("#main: found the answer")
    assert target == "main"
    assert body == "found the answer"


def test_parse_route_mid_sentence():
    target, body = parse_route("I'm blocked, #human: need help")
    assert target == "human"
    assert body == "need help"


def test_parse_route_with_context():
    target, body = parse_route("After analysis, #research: pytest wins")
    assert target == "research"
    assert body == "pytest wins"


def test_parse_route_no_match():
    target, body = parse_route("normal message without routing")
    assert target is None
    assert body == "normal message without routing"


def test_parse_route_hashtag_but_no_colon():
    target, body = parse_route("discussing #main channel")
    assert target is None
    assert body == "discussing #main channel"


def test_format_stub_short():
    stub = format_stub("main", "short message")
    assert stub == "→ #main: short message"


def test_format_stub_long():
    long_msg = "a" * 100
    stub = format_stub("main", long_msg, max_len=50)
    assert stub == f"→ #main: {'a' * 50}..."
    assert len(stub) < len(long_msg) + 20
