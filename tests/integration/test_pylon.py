"""Pylon integration test - Two agents messaging through the grid."""

import asyncio
import websockets
import pytest
from protoss.pylon import Pylon


async def fake_agent(agent_id: str, target_id: str, message: str):
    """Fake agent that connects and sends one message."""
    uri = f"ws://localhost:8229/{agent_id}"

    async with websockets.connect(uri) as websocket:
        print(f"[{agent_id}] Connected to Pylon")

        # Send message
        psi_msg = f"§PSI:{target_id}:{agent_id}:report:{message}"
        await websocket.send(psi_msg)
        print(f"[{agent_id}] Sent: {psi_msg}")

        # Listen for incoming
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
            print(f"[{agent_id}] Received: {response}")
        except asyncio.TimeoutError:
            print(f"[{agent_id}] No response received")


@pytest.mark.asyncio
async def test_pylon_routing():
    """Test basic Pylon message routing."""

    # Start Pylon
    pylon = Pylon(port=8229)
    await pylon.start()
    print("🔹 Pylon grid online")

    try:
        # Give Pylon a moment to start
        await asyncio.sleep(0.5)

        # Launch two agents concurrently
        await asyncio.gather(
            fake_agent("zealot-a", "zealot-b", "hello-from-alpha"),
            fake_agent("zealot-b", "zealot-a", "hello-from-beta"),
        )

        print("✅ Pylon integration test complete")
    finally:
        await pylon.stop()


if __name__ == "__main__":
    asyncio.run(test_pylon_routing())
