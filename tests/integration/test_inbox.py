"""Test Pylon inbox functionality with offline message queuing."""

import asyncio
import websockets
import pytest
from protoss.structures.pylon import Pylon, Psi


async def offline_agent_test():
    """Test message queuing for offline agents."""

    # Start Pylon
    pylon = Pylon(port=8232)
    await pylon.start()
    print("🔹 Pylon grid online for inbox test")

    try:
        await asyncio.sleep(0.5)

        # Send message to offline agent "zealot-alpha"
        test_message = Psi(
            target="zealot-alpha",
            source="test-sender",
            type="command",
            content="Execute when you come online",
        )

        # Put message directly into Pylon routing
        await pylon.message_queue.put(test_message)
        print("🔹 Sent message to offline zealot-alpha")

        # Let routing process
        await asyncio.sleep(0.2)

        # Check if message was queued in inbox
        assert "zealot-alpha" in pylon.inbox
        assert len(pylon.inbox["zealot-alpha"]) == 1
        assert pylon.inbox["zealot-alpha"][0].content == "Execute when you come online"
        print("🔹 Message queued in inbox - SUCCESS")

        # Now agent comes online and connects
        uri = "ws://localhost:8232/zealot-alpha"
        received_messages = []

        async with websockets.connect(uri) as websocket:
            print("🔹 zealot-alpha connected - should receive queued message")

            # Wait for flushed message
            message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            received_messages.append(message)
            print(f"🔹 Received: {message}")

        # Verify message delivery
        assert len(received_messages) == 1
        assert "Execute when you come online" in received_messages[0]

        # Verify inbox was cleared
        assert "zealot-alpha" not in pylon.inbox
        print("✅ Inbox test complete - offline queuing works!")

    finally:
        await pylon.stop()


@pytest.mark.asyncio
async def test_inbox_queuing():
    """Pytest version of inbox test."""
    await offline_agent_test()


if __name__ == "__main__":
    asyncio.run(offline_agent_test())
