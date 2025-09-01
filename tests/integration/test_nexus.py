"""Nexus integration test - Full Protoss coordination flow."""

import asyncio
import pytest
from protoss.nexus import Nexus


@pytest.mark.asyncio
async def test_nexus_coordination():
    """Test complete Nexus → Gateway → Zealot → Pylon flow."""

    # Initialize Nexus
    nexus = Nexus(pylon_port=8230)
    await nexus.start()

    try:
        await asyncio.sleep(0.5)  # Let grid stabilize

        # Execute task through full Protoss stack
        result = await nexus.execute_task("What color is the sky?")

        print("✅ Nexus coordination complete")
        print(f"📋 Task result: {result}")

        assert "blue" in result.lower()
        return result
    finally:
        await nexus.pylon.stop()


if __name__ == "__main__":
    asyncio.run(test_nexus_coordination())
