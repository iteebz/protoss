
import asyncio
import pytest
import subprocess
import sys
import time
import websockets
from threading import Thread
import json

from protoss.core.bus import Bus, Message
from protoss.core.config import Config

# --- Fixtures for Bus Server ---

@pytest.fixture(scope="module")
def event_loop():
    """Ensure a new event loop for the module scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def bus_server(event_loop):
    """Starts a Bus server in a separate thread and yields its URL."""
    bus_port = 8765  # Use a different port to avoid conflicts
    bus_url = f"ws://localhost:{bus_port}"
    bus_instance = Bus(port=bus_port)

    async def start_server():
        await bus_instance.start()

    async def stop_server():
        await bus_instance.stop()

    # Start the server in the event loop
    event_loop.run_until_complete(start_server())

    # Wait for the server to start
    for _ in range(10):
        try:
            event_loop.run_until_complete(websockets.connect(bus_url, open_timeout=1))
            break
        except (websockets.exceptions.ConnectionClosedOK, ConnectionRefusedError):
            time.sleep(0.1)
    else:
        pytest.fail("Bus server did not start in time.")

    yield bus_url, bus_instance # Yield both URL and instance for assertions

    # Teardown: Stop the bus server
    event_loop.run_until_complete(stop_server())


# --- Integration Test ---

@pytest.mark.asyncio
async def test_unit_connects_and_despawns(bus_server):
    """
    Tests that a Unit process can connect to a running Bus, receive a task,
    and then despawn gracefully, proving the pure contract.
    """
    bus_url, bus_instance = bus_server
    agent_id = "zealot-full-test-1"
    channel_id = "full-test-channel"
    task = "Connect to the bus and then immediately despawn by returning '!despawn'."

    # Create a Config object for the agent
    agent_config = Config(bus_url=bus_url)
    config_json = json.dumps(agent_config.to_dict())

    # Ensure the channel exists on the bus for later assertions
    bus_instance._ensure_channel(channel_id)

    command = [
        sys.executable,
        "-m",
        "protoss.agents.unit",
        "--agent-id",
        agent_id,
        "--agent-type",
        "zealot",
        "--channel",
        channel_id,
        "--bus-url", # Re-add bus_url as a separate argument
        bus_url,
        "--task", # Re-add task as a separate argument
        task,
        "--config-json",
        config_json,
    ]

    # Run the Unit as a subprocess
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Wait for the agent to connect and despawn
    # We'll poll the bus_instance to check for agent registration/deregistration
    connected = False
    despawned = False
    start_time = time.time()
    timeout = 10 # seconds

    while time.time() - start_time < timeout:
        if agent_id in bus_instance.channels[channel_id].subscribers:
            connected = True
        if agent_id not in bus_instance.channels[channel_id].subscribers and connected:
            despawned = True
            break
        await asyncio.sleep(0.1) # Non-blocking sleep

    # Wait for the process to terminate and check its exit code
    stdout, stderr = process.communicate(timeout=15)
    # Assertions
    print(f"\nAgent stdout: {stdout}")
    assert process.returncode == 0, f"Agent process exited with non-zero code {process.returncode}. Stderr: {stderr}"

    print(f"Agent stdout: {stdout}")
    print(f"Agent stderr: {stderr}")

    # Optional: Check bus history for despawn message
    despawn_message_found = False
    for msg in bus_instance.channels[channel_id].history:
        if msg.sender == agent_id and "despawn" in msg.content.lower():
            despawn_message_found = True
            break
    assert despawn_message_found, "Despawn message not found in bus history."
