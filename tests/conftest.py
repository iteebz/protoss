"""Constitutional test fixtures - beautiful mocking."""

import pytest
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def bus():
    """Clean Bus mock."""
    mock = Mock()
    mock.start = AsyncMock()
    mock.stop = AsyncMock()
    mock.transmit = AsyncMock()
    mock.history = Mock(return_value=[])
    mock.channels = {}
    mock.server = Mock()
    mock.server.stop = AsyncMock()
    return mock


@pytest.fixture
def gateway():
    """Clean Gateway mock."""
    mock = Mock()
    mock.start = AsyncMock()
    mock.stop = AsyncMock()
    mock._spawn_process = AsyncMock()
    return mock


@pytest.fixture
def config():
    """Test config."""
    from protoss.core.config import Config

    return Config(port=9999)


@pytest.fixture
def message():
    """Test message."""
    from protoss.core.message import Message

    return Message("test", "agent", "content")


@pytest.fixture
def mock_websockets():
    """Mock websockets.serve for Bus lifecycle tests."""
    mock_server = AsyncMock()
    mock_server.close = AsyncMock()
    mock_server.wait_closed = AsyncMock()

    async def serve_mock(*args, **kwargs):
        return mock_server

    return serve_mock, mock_server


@pytest.fixture
def mock_khala():
    """Sacred Khala mock for constitutional testing."""
    mock = AsyncMock()
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    mock.send = AsyncMock()
    mock.receive = AsyncMock()
    mock.listen = AsyncMock()
    mock.request_history = AsyncMock(return_value=[])
    return mock
