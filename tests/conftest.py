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


@pytest.fixture(autouse=True)
def cleanup_khala_state():
    """Clean up Khala singleton state between tests."""
    from protoss.khala import khala

    # Clear in-memory state
    khala.subscribers.clear()
    khala.memories.clear()
    khala.agents.clear()

    yield

    # Post-test cleanup
    khala.subscribers.clear()
    khala.memories.clear()
    khala.agents.clear()


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
