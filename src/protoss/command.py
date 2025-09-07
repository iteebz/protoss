#!/usr/bin/env python3
"""Protoss command interface."""

import asyncio
import sys
from protoss import Nexus


async def main():
    if len(sys.argv) < 2:
        print("Usage: python -m protoss.command 'COMMAND'")
        return

    task = sys.argv[1]

    nexus = Nexus()
    await nexus.start()

    try:
        print(f"🔹 COMMANDING ZEALOT: {task}")
        result = await nexus.execute_task(task)
        print(f"🔹 ZEALOT RESPONSE: {result}")
    finally:
        await nexus.pylon.stop()


if __name__ == "__main__":
    asyncio.run(main())
