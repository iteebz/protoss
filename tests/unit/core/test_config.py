"""Unit tests for Config."""


def test_config_derives_url():
    """Config derives bus_url from port."""
    from protoss.core.config import Config

    config = Config(port=8000)
    assert config.bus_url == "ws://localhost:8000"


def test_config_dict_conversion():
    """Config converts to/from dict cleanly."""
    from protoss.core.config import Config

    config = Config(port=9000, debug=True)
    data = config.to_dict()

    assert data["port"] == 9000
    assert data["debug"] is True

    restored = Config.from_dict(data)
    assert restored.port == 9000
    assert restored.debug is True
