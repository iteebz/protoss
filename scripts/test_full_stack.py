#!/usr/bin/env python3
"""Test agents building a full-stack app with tests and QA."""

import asyncio
import logging
import uuid
from src.protoss.swarm import Swarm

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def test_full_stack():
    """Test agents building a full-stack app with proper testing."""
    
    run_id = uuid.uuid4().hex[:8]
    channel = f"fullstack-{run_id}"
    base_dir = f"./test-run-{run_id}"
    
    swarm = Swarm(channel=channel, base_dir=base_dir)
    
    print(f"Full-stack coordination in #{channel} using sandbox: {base_dir}")
    
    # Complex multi-file project with testing requirements
    await swarm.send_human_message("""
Build a simple todo list web application with these requirements:

BACKEND:
- Python Flask API with endpoints: GET /todos, POST /todos, DELETE /todos/<id>
- JSON data storage in todos.json file
- Proper error handling and validation
- Unit tests for all endpoints using pytest

FRONTEND:
- HTML/CSS/JS single page app
- Add todo functionality with input validation
- Delete todo functionality
- Responsive design
- Integration tests that verify frontend talks to backend

PROJECT STRUCTURE:
- app.py (Flask backend)
- static/index.html (frontend)
- static/style.css (styling)  
- static/script.js (frontend logic)
- test_app.py (backend tests)
- test_integration.py (integration tests)
- requirements.txt (dependencies)

TESTING:
- All tests must pass
- Backend tests with pytest
- Integration tests that start server and test actual HTTP calls
- Test coverage for edge cases

Coordinate who builds what, ensure proper testing, and signal !complete when all tests pass.
""")
    
    # Start the swarm
    await swarm.start()
    
    # Give them more time for complex build
    await asyncio.sleep(120)
    
    # Show the coordination conversation
    conversation = swarm.get_conversation(channel)
    
    print(f"\n=== FULL-STACK COORDINATION ===")
    for msg in conversation[-10:]:  # Show last 10 messages
        sender = msg['sender'].upper() if msg['sender'] != 'human' else 'HUMAN'
        content = msg['content'][:300] + "..." if len(msg['content']) > 300 else msg['content']
        print(f"\n{sender}: {content}")
    
    # Check for completion
    complete_signals = [msg for msg in conversation if "!complete" in msg['content'].lower()]
    print(f"\nCompletion signals: {len(complete_signals)}")

if __name__ == "__main__":
    asyncio.run(test_full_stack())