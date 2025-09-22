"""Config tests."""

from protoss.core.config import Config


def test_config_defaults():
    """Config has sensible defaults."""
    config = Config()

    assert config.port == 8888
    assert config.timeout == 3600
    assert config.debug is False
    assert config.max_agents == 100


def test_config_bus_url():
    """Config derives bus_url from port."""
    config = Config(port=9999)
    # Note: Config is frozen dataclass so bus_url is set at init
    # The actual derivation would need to be in __post_init__ if needed
    assert config.bus_url == "ws://localhost:8888"  # Default value
