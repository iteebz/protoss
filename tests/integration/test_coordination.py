"""Test real swarm coordination scenarios with inbox queuing."""

import asyncio
import websockets
from protoss import Nexus, Gateway
from protoss.structures.pylon import Pylon, Psi


async def busy_agent_coordination():
    """Test: Agent working on long task receives queued messages from others."""

    # Start infrastructure
    pylon = Pylon(port=8233)
    await pylon.start()
    print("🔹 Pylon grid online for swarm test")

    try:
        await asyncio.sleep(0.5)

        # Simulate busy agent scenario
        print("🔹 Simulating zealot-worker on long task...")

        # Send multiple messages while agent is "busy" (offline)
        messages = [
            Psi("zealot-worker", "zealot-alpha", "update", "Task 1 complete"),
            Psi("zealot-worker", "zealot-beta", "data", "Processing results: [1,2,3]"),
            Psi("zealot-worker", "council", "priority", "Critical: Review needed"),
        ]

        # Queue all messages while worker is busy
        for msg in messages:
            await pylon.message_queue.put(msg)
            print(f"🔹 Queued: {msg.source} → {msg.target}: {msg.content}")

        # Let routing process
        await asyncio.sleep(0.3)

        # Verify all messages queued in correct inbox
        assert "zealot-worker" in pylon.inbox
        assert len(pylon.inbox["zealot-worker"]) == 3
        print("🔹 All 3 messages queued for busy worker")

        # Worker comes online - should receive all queued messages in FIFO order
        received = []
        uri = "ws://localhost:8233/zealot-worker"

        async with websockets.connect(uri) as websocket:
            print("🔹 zealot-worker came online - receiving backlog...")

            # Receive all queued messages
            for i in range(3):
                message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                received.append(message)
                print(f"🔹 Received {i+1}: {message}")

        # Verify FIFO order maintained
        assert "Task 1 complete" in received[0]
        assert "Processing results" in received[1]
        assert "Critical: Review needed" in received[2]

        # Verify inbox cleared
        assert "zealot-worker" not in pylon.inbox

        print("✅ Busy agent coordination test - SUCCESS!")

    finally:
        await pylon.stop()


async def multi_agent_concurrent_inboxes():
    """Test: Multiple agents each with separate inbox queues."""

    pylon = Pylon(port=8234)
    await pylon.start()
    print("🔹 Testing concurrent agent inboxes...")

    try:
        await asyncio.sleep(0.5)

        # Send messages to 3 different offline agents
        agent_messages = {
            "zealot-alpha": ["Task A1", "Task A2"],
            "zealot-beta": ["Task B1", "Task B2", "Task B3"],
            "zealot-gamma": ["Task G1"],
        }

        # Queue messages for all agents
        for agent_id, tasks in agent_messages.items():
            for i, task in enumerate(tasks):
                msg = Psi(agent_id, "coordinator", "task", task)
                await pylon.message_queue.put(msg)
                print(f"🔹 Queued for {agent_id}: {task}")

        await asyncio.sleep(0.3)

        # Verify each agent has correct inbox
        assert len(pylon.inbox["zealot-alpha"]) == 2
        assert len(pylon.inbox["zealot-beta"]) == 3
        assert len(pylon.inbox["zealot-gamma"]) == 1
        print("🔹 All agent inboxes populated correctly")

        # Agents connect concurrently and receive their messages
        async def agent_connect(agent_id, expected_count):
            uri = f"ws://localhost:8234/{agent_id}"
            received = []

            async with websockets.connect(uri) as websocket:
                for i in range(expected_count):
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    received.append(message)

            print(f"🔹 {agent_id} received {len(received)} messages")
            return received

        # All agents connect simultaneously
        alpha_msgs, beta_msgs, gamma_msgs = await asyncio.gather(
            agent_connect("zealot-alpha", 2),
            agent_connect("zealot-beta", 3),
            agent_connect("zealot-gamma", 1),
        )

        # Verify correct message counts
        assert len(alpha_msgs) == 2
        assert len(beta_msgs) == 3
        assert len(gamma_msgs) == 1

        # Verify inboxes cleared
        assert len(pylon.inbox) == 0

        print("✅ Multi-agent concurrent inboxes - SUCCESS!")

    finally:
        await pylon.stop()


async def real_zealot_coordination():
    """Test: Actual Zealot agents coordinating via inbox system."""

    nexus = Nexus(pylon_port=8235)
    await nexus.start()

    try:
        # Start a long-running Zealot task in background
        gateway = Gateway(pylon_port=8235)

        print("🔹 Starting long-running Zealot task...")

        # This would be a real coordination scenario
        task = "Create a file called status.txt, then wait for further instructions"
        zealot_task = asyncio.create_task(gateway.spawn_zealot(task, target="nexus"))

        # Give zealot time to start working
        await asyncio.sleep(1.0)

        # Send coordination messages while zealot works
        coordination_messages = [
            Psi("zealot-worker", "coordinator", "status", "Phase 1 complete"),
            Psi("zealot-worker", "coordinator", "next", "Proceed to phase 2"),
        ]

        for msg in coordination_messages:
            await nexus.pylon.message_queue.put(msg)

        print("🔹 Sent coordination messages to working Zealot")

        # Wait for zealot to complete
        await zealot_task

        print("✅ Real Zealot coordination test complete!")

    finally:
        await nexus.pylon.stop()


if __name__ == "__main__":
    print("🔹 Running swarm coordination tests...\n")

    asyncio.run(busy_agent_coordination())
    print()
    asyncio.run(multi_agent_concurrent_inboxes())
    print()
    asyncio.run(real_zealot_coordination())
