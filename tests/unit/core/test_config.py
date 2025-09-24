"""Config contract tests."""

from protoss.core.config import Config


def test_defaults(config: Config):
    assert config.port == 8888
    assert config.timeout == 3600
    assert config.max_units == 100
    assert config.bus_url == "ws://localhost:8888"


def test_overrides_respected():
    custom = Config(port=7777, debug=True, bus_url="ws://bus:7777")
    assert custom.port == 7777
    assert custom.debug is True
    assert custom.bus_url == "ws://bus:7777"
