
import subprocess
import sys

def test_spawn_zealot_process():
    """
    Test that a Zealot unit can be spawned as a standalone process.

    This test simulates the Gateway's action of spawning a new agent.
    It executes the `unit.py` script as a subprocess and checks for a
    successful (or expected failure) exit code.
    """
    command = [
        sys.executable,
        "-m",
        "protoss.agents.unit",
        "--agent-id",
        "zealot-test-spawn-1",
        "--agent-type",
        "zealot",
        "--channel",
        "test-spawn-channel",
        "--bus-url",
        "ws://localhost:9999", # A dummy URL, connection will fail
        "--task",
        "Test the spark of life.",
    ]

    # We expect this to fail to connect, but the script should start
    # and run until the connection error. A clean exit or a specific
    # error code related to connection is a success for this test.
    # A non-zero exit code is expected.
    result = subprocess.run(command, capture_output=True, text=True)

    # Check that the process ran and exited.
    # A non-zero exit code is okay, as long as it's not from a syntax error.
    # We check stderr for the expected connection error.
    assert "Connect call failed" in result.stderr
