#!/usr/bin/env python3
"""Debug cogency agent responses."""

import asyncio
import logging
import cogency

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

async def test_cogency():
    """Test basic cogency agent."""
    
    agent = cogency.Agent(
        llm="gemini",
        instructions="You are a test agent. Respond briefly to messages.",
        base_dir="./debug-test"
    )
    
    print("Testing cogency agent...")
    
    async for event in agent("Hello, can you respond?"):
        print(f"Event: {event}")
        if event["type"] == "respond":
            print(f"Response: {event['content']}")
            break

if __name__ == "__main__":
    asyncio.run(test_cogency())