"""Gateway integration test - Spawn Zealot, execute task, report via Pylon."""

import asyncio
import pytest
import websockets
from protoss.pylon import Pylon
from protoss.gateway import Gateway


async def nexus_listener():
    """Fake Nexus that listens for Zealot reports."""
    uri = "ws://localhost:8231/nexus"

    async with websockets.connect(uri) as websocket:
        print("[NEXUS] Connected to Pylon grid")

        # Wait for Zealot report
        message = await websocket.recv()
        print(f"[NEXUS] Received: {message}")

        return message


@pytest.mark.asyncio
async def test_gateway_spawn():
    """Test Gateway spawning Zealot that reports to Nexus."""

    # Start Pylon grid
    pylon = Pylon(port=8231)
    await pylon.start()
    print("🔹 Pylon grid online")

    try:
        await asyncio.sleep(0.5)  # Let Pylon start

        # Start Gateway
        gateway = Gateway(pylon_host="localhost", pylon_port=8231)

        # Run concurrently: Nexus listening + Gateway spawning Zealot
        nexus_task = asyncio.create_task(nexus_listener())

        await asyncio.sleep(0.1)  # Let Nexus connect first

        # Spawn Zealot with simple task
        zealot_id = await gateway.spawn_zealot("What is 2+2?", target="nexus")

        # Wait for completion
        result = await nexus_task

        print(f"✅ Gateway test complete - Zealot {zealot_id} executed and reported")
        print(f"📋 Result: {result}")

        assert "4" in result
    finally:
        await pylon.stop()


if __name__ == "__main__":
    import websockets

    asyncio.run(test_gateway_spawn())
