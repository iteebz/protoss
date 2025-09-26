from unittest.mock import patch, AsyncMock, MagicMock

from typer.testing import CliRunner

from protoss.cli import app

runner = CliRunner()


@patch("protoss.cli.coordinate")
def test_coord_invokes_coordination(mock_coordinate):
    """Verify the 'coord' command parses arguments and calls the core function."""
    result = runner.invoke(
        app,
        [
            "coord",
            "test vision",
            "--port",
            "9999",
            "--coordination-id",
            "test-coord-123",
        ],
    )

    assert result.exit_code == 0
    mock_coordinate.assert_called_once_with("test vision", 9999, "test-coord-123")


@patch("protoss.cli.Khala")
def test_status_displays_status(mock_khala_class):
    """Verify the 'status' command displays the bus status correctly."""
    # Arrange
    mock_khala_instance = mock_khala_class.return_value
    mock_khala_instance.connect = AsyncMock()
    mock_khala_instance.disconnect = AsyncMock()
    mock_khala_instance.send = AsyncMock()

    # Simulate a status response from the bus
    status_payload = {
        "type": "status_resp",
        "channel": "system",
        "sender": "bus",
        "event": {
            "status": "online",
            "bus": {"channels": 5, "agents": 10, "messages": 100},
        },
    }
    # Fix: receive is awaited, so it must be an AsyncMock
    mock_khala_instance.receive = AsyncMock(
        return_value=MagicMock(msg_type="status_resp", event=status_payload["event"])
    )

    # Act
    result = runner.invoke(app, ["status"])

    # Assert
    assert result.exit_code == 0
    assert "Protoss Status" in result.stdout
    assert "Status: online" in result.stdout
    assert "Bus metrics: channels=5 agents=10 messages=100" in result.stdout
    mock_khala_instance.connect.assert_awaited_once()
    mock_khala_instance.disconnect.assert_awaited_once()


@patch("protoss.cli.uuid4")
@patch("protoss.cli.Khala")
def test_ask_sends_and_prints(mock_khala_class, mock_uuid):
    """Verify the 'ask' command sends a question and prints the response."""
    # Arrange
    mock_uuid.return_value = MagicMock(hex="fixeduuid")
    # Fix: The cli slices the hex to 8 characters, so we must match that
    expected_channel = f"query:{mock_uuid.return_value.hex[:8]}:active"

    mock_khala_instance = mock_khala_class.return_value
    mock_khala_instance.connect = AsyncMock()
    mock_khala_instance.disconnect = AsyncMock()
    mock_khala_instance.send = AsyncMock()

    # Simulate an arbiter response
    async def listen_generator():
        yield MagicMock(
            msg_type="agent_message",
            channel=expected_channel,
            sender="arbiter-abc",
            event={"content": "The swarm is ready."},
        )

    mock_khala_instance.listen.return_value = listen_generator()

    # Act
    result = runner.invoke(app, ["ask", "Is the swarm ready?"])

    # Assert
    assert result.exit_code == 0
    assert f"Asking swarm in channel {expected_channel}..." in result.stdout
    assert "Human: Is the swarm ready?" in result.stdout
    assert "ARBITER: The swarm is ready." in result.stdout

    # Verify that send was called with the correct question
    mock_khala_instance.send.assert_awaited_once()
    sent_data = mock_khala_instance.send.call_args[0][0]
    assert sent_data["type"] == "human_ask"
    assert sent_data["channel"] == expected_channel
    assert "Is the swarm ready? @arbiter" in sent_data["content"]
