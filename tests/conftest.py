"""Pytest configuration for PROTOSS test suite.

Provides shared fixtures and configuration for testing coordination patterns.
Ensures test isolation and proper cleanup of infrastructure resources.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

# Configure pytest-asyncio for async test support
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_protoss_dir():
    """Create temporary directory for test artifacts."""
    temp_dir = tempfile.mkdtemp(prefix="protoss_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def bus():
    """Create fresh Bus instance for testing."""
    from protoss.core.bus import Bus

    bus_instance = Bus()
    yield bus_instance

    # Cleanup after test
    if hasattr(bus_instance, "_server") and bus_instance._server:
        asyncio.run(bus_instance.stop())


@pytest.fixture
def config():
    """Create fresh Config instance for testing."""
    from protoss.core.config import Config

    return Config(debug=True, timeout=5)


@pytest.fixture
def mock_bus():
    """Create mock Bus for unit testing."""
    from unittest.mock import AsyncMock, Mock

    mock = Mock()
    mock.transmit = AsyncMock()
    mock.register = Mock()
    mock.history = Mock(return_value=[])
    mock.channels = {}
    mock.memories = {}
    mock.start = AsyncMock()
    mock.stop = AsyncMock()

    return mock


@pytest.fixture
def mock_channel():
    """Create mock channel with messages for testing."""
    from protoss.core.bus import Bus, Message

    bus = Bus()
    channel_id = "test-channel"

    # Add some test messages
    msg1 = Message(channel_id, "agent1", "First message")
    msg2 = Message(channel_id, "agent2", "Second message")
    msg3 = Message(channel_id, "agent3", "Third message")

    bus.memories[channel_id] = [msg1, msg2, msg3]

    return {"bus": bus, "channel_id": channel_id, "messages": [msg1, msg2, msg3]}


# Test configuration
def pytest_configure(config):
    """Configure pytest for PROTOSS testing."""
    # Add custom markers
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers."""
    for item in items:
        # Mark async tests that use infrastructure as integration tests
        if "test_infrastructure" in item.fixturenames:
            item.add_marker(pytest.mark.integration)

        # Mark tests with long sleep times as slow
        if hasattr(item, "function") and item.function.__code__:
            source = item.function.__code__.co_consts
            if any(
                isinstance(const, (int, float)) and const >= 5 for const in source or []
            ):
                item.add_marker(pytest.mark.slow)
