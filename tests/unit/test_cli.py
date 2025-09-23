"""Unit tests for the Protoss CLI."""

import os
import shutil
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, mock_open, Mock
import signal

from protoss.cli import app, PROTOSS_DIR, BUS_PID_FILE, _stop_process


runner = CliRunner()


@pytest.fixture(autouse=True)
def clean_protoss_dir():
    """Ensure a clean .protoss directory for each test."""
    if os.path.exists(PROTOSS_DIR):
        shutil.rmtree(PROTOSS_DIR)
    os.makedirs(PROTOSS_DIR, exist_ok=True)


# --- Tests for 'start' command --- #


@patch("protoss.cli.stop")
@patch("signal.pause")
@patch("signal.signal")
@patch("time.sleep")
@patch("subprocess.Popen")
@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
def test_start_command_success(
    mock_makedirs,
    mock_open_file,
    mock_popen,
    mock_sleep,
    mock_signal,
    mock_pause,
    mock_stop,
):
    """Test that the start command successfully launches bus."""
    mock_bus_process = Mock()
    mock_bus_process.pid = 12345
    mock_popen.return_value = mock_bus_process

    result = runner.invoke(app, ["start"])

    assert result.exit_code == 0
    assert "Bus started with PID 12345" in result.stdout
    assert "Protoss infrastructure is running" in result.stdout

    mock_makedirs.assert_called_once_with(PROTOSS_DIR, exist_ok=True)

    # Check PID file writes
    mock_open_file.assert_called_once_with(BUS_PID_FILE, "w")
    mock_open_file().write.assert_called_once_with("12345")

    # Check subprocess calls
    mock_popen.assert_called_once_with(
        ["python", "-m", "src.protoss.cli", "bus", "--port=8888"]
    )
    mock_pause.assert_called_once()


# --- Tests for 'stop' command and its helper --- #


@patch("protoss.cli._stop_process")
def test_stop_command_calls_helpers(mock_stop_helper):
    """Test that the main 'stop' command calls its helper for each process."""
    result = runner.invoke(app, ["stop"])

    assert result.exit_code == 0
    mock_stop_helper.assert_called_once_with("Protoss Bus", BUS_PID_FILE)


@patch("os.remove")
@patch("os.kill")
@patch("builtins.open", new_callable=mock_open, read_data="12345")
@patch("os.path.exists", return_value=True)
def test_stop_process_helper_success(
    mock_exists, mock_open, mock_kill, mock_remove, capsys
):
    """Test the _stop_process helper successfully stopping a process."""
    _stop_process("Test Process", "/fake/pid.file")

    captured = capsys.readouterr()
    assert "Test Process (PID 12345) stopped." in captured.out

    mock_exists.assert_called_with("/fake/pid.file")
    mock_open.assert_called_once_with("/fake/pid.file", "r")
    mock_kill.assert_called_once_with(12345, signal.SIGTERM)
    mock_remove.assert_called_once_with("/fake/pid.file")


@patch("os.remove")
@patch("os.kill", side_effect=ProcessLookupError)
@patch("builtins.open", new_callable=mock_open, read_data="12345")
@patch("os.path.exists", return_value=True)
def test_stop_process_helper_not_running(
    mock_exists, mock_open, mock_kill, mock_remove, capsys
):
    """Test the _stop_process helper when the process is already dead."""
    _stop_process("Test Process", "/fake/pid.file")

    captured = capsys.readouterr()
    assert "Test Process (PID 12345) was not running." in captured.out

    mock_kill.assert_called_once_with(12345, signal.SIGTERM)
    mock_remove.assert_called_once_with("/fake/pid.file")  # Should still be removed


@patch("os.remove")
@patch("os.kill")
@patch("os.path.exists", return_value=False)
def test_stop_process_helper_no_pid_file(mock_exists, mock_kill, mock_remove, capsys):
    """Test the _stop_process helper when the PID file does not exist."""
    _stop_process("Test Process", "/fake/pid.file")

    captured = capsys.readouterr()
    assert captured.out == ""

    mock_kill.assert_not_called()
    mock_remove.assert_not_called()
