"""Tests for the SQLite storage layer."""

import asyncio
import time
from pathlib import Path

import pytest

from src.protoss.lib.sqlite import SQLite


@pytest.fixture
def temp_base_dir(tmp_path: Path) -> str:
    """Create a temporary base directory for isolated test runs."""
    return str(tmp_path)


@pytest.mark.asyncio
async def test_save_and_load_messages(temp_base_dir: str):
    """Verify that messages can be saved and loaded correctly."""
    storage = SQLite(base_dir=temp_base_dir)
    channel = "test_channel"
    sender = "test_sender"
    content = "test_content"
    timestamp1 = time.time()

    # 1. Save a message
    await storage.save_message(channel, sender, content, timestamp1)

    # 2. Load messages and verify the saved message is present
    messages = await storage.load_messages(channel)
    assert len(messages) == 1
    assert messages[0]["sender"] == sender
    assert messages[0]["content"] == content
    assert messages[0]["timestamp"] == timestamp1


@pytest.mark.asyncio
async def test_load_messages_with_since(temp_base_dir: str):
    """Verify that the 'since' parameter correctly filters messages."""
    storage = SQLite(base_dir=temp_base_dir)
    channel = "test_channel"
    timestamp1 = time.time()

    # 1. Save the first message
    await storage.save_message(channel, "sender1", "content1", timestamp1)

    # Ensure a different timestamp for the second message
    await asyncio.sleep(0.01)
    timestamp2 = time.time()

    # 2. Save the second message
    await storage.save_message(channel, "sender2", "content2", timestamp2)

    # 3. Load messages since the first timestamp
    messages_since = await storage.load_messages(channel, since=timestamp1)

    # 4. Verify that only the second message is returned
    assert len(messages_since) == 1
    assert messages_since[0]["sender"] == "sender2"
    assert messages_since[0]["timestamp"] == timestamp2

    # 5. Verify loading all messages still works
    all_messages = await storage.load_messages(channel)
    assert len(all_messages) == 2


@pytest.mark.asyncio
async def test_start_run_creates_record(temp_base_dir):
    """start_run should create a run record with started_at timestamp."""
    storage = SQLite(base_dir=temp_base_dir)

    run_id = "test-run-1"
    task = "Build a system"
    agents = ["zealot", "sentinel", "harbinger"]
    channel = "human"

    await storage.start_run(run_id, task, agents, channel)

    # Verify by listing runs
    runs = await storage.list_runs(limit=10)
    assert len(runs) == 1
    assert runs[0]["id"] == run_id
    assert runs[0]["task"] == task
    assert runs[0]["agents"] == "zealot,sentinel,harbinger"
    assert runs[0]["channel"] == channel
    assert runs[0]["started_at"] is not None
    assert runs[0]["completed_at"] is None


@pytest.mark.asyncio
async def test_complete_run_updates_record(temp_base_dir):
    """complete_run should update run with outcome and message count."""
    storage = SQLite(base_dir=temp_base_dir)

    run_id = "test-run-2"
    await storage.start_run(run_id, "Test task", ["zealot"], "human")

    # Complete the run
    await storage.complete_run(run_id, "success", 42)

    runs = await storage.list_runs()
    assert len(runs) == 1
    assert runs[0]["id"] == run_id
    assert runs[0]["completed_at"] is not None
    assert runs[0]["outcome"] == "success"
    assert runs[0]["message_count"] == 42


@pytest.mark.asyncio
async def test_run_lifecycle_complete(temp_base_dir):
    """Full lifecycle: create, verify pending, complete, verify final."""
    storage = SQLite(base_dir=temp_base_dir)

    run_id = "lifecycle-test"
    task = "Test lifecycle"
    agents = ["zealot", "sentinel"]

    # Start
    await storage.start_run(run_id, task, agents, "human")

    # Verify started
    runs = await storage.list_runs()
    assert len(runs) == 1
    assert runs[0]["completed_at"] is None

    # Complete
    await storage.complete_run(run_id, "timeout", 100)

    # Verify completed
    runs = await storage.list_runs()
    assert runs[0]["completed_at"] is not None
    assert runs[0]["outcome"] == "timeout"
    assert runs[0]["message_count"] == 100


@pytest.mark.asyncio
async def test_list_runs_respects_limit(temp_base_dir):
    """list_runs should respect limit parameter."""
    storage = SQLite(base_dir=temp_base_dir)

    # Create multiple runs
    for i in range(5):
        await storage.start_run(f"run-{i}", f"Task {i}", ["zealot"], "human")

    # List with limit
    runs = await storage.list_runs(limit=2)
    assert len(runs) <= 2


@pytest.mark.asyncio
async def test_list_runs_returns_recent_first(temp_base_dir):
    """list_runs should return most recent runs first."""
    storage = SQLite(base_dir=temp_base_dir)

    # Create runs with identifiable IDs
    ids = []
    for i in range(3):
        run_id = f"run-{i}"
        ids.append(run_id)
        await storage.start_run(run_id, f"Task {i}", ["zealot"], "human")
        await asyncio.sleep(0.01)  # Ensure different timestamps

    runs = await storage.list_runs(limit=10)

    # Should be in reverse order (most recent first)
    assert runs[0]["id"] == "run-2"
    assert runs[1]["id"] == "run-1"
    assert runs[2]["id"] == "run-0"


@pytest.mark.asyncio
async def test_run_agents_stored_as_csv(temp_base_dir):
    """Agent list should be stored as comma-separated string."""
    storage = SQLite(base_dir=temp_base_dir)

    agents = ["zealot", "sentinel", "harbinger"]
    await storage.start_run("test", "task", agents, "human")

    runs = await storage.list_runs()
    assert runs[0]["agents"] == "zealot,sentinel,harbinger"


@pytest.mark.asyncio
async def test_run_with_single_agent(temp_base_dir):
    """Should handle single agent correctly."""
    storage = SQLite(base_dir=temp_base_dir)

    await storage.start_run("single", "task", ["zealot"], "human")

    runs = await storage.list_runs()
    assert runs[0]["agents"] == "zealot"


@pytest.mark.asyncio
async def test_ledger_and_runs_coexist(temp_base_dir):
    """Ledger and runs tables should not interfere."""
    storage = SQLite(base_dir=temp_base_dir)

    # Add messages to ledger
    await storage.save_message("test_channel", "human", "hello", 123.456)

    # Add run record
    await storage.start_run("run-1", "task", ["zealot"], "test_channel")

    # Verify both exist
    messages = await storage.load_messages("test_channel")
    assert len(messages) == 1

    runs = await storage.list_runs()
    assert len(runs) == 1

    # Different tables, no pollution
    assert messages[0]["sender"] == "human"
    assert runs[0]["id"] == "run-1"


@pytest.mark.asyncio
async def test_run_timestamps_are_iso_formatted(temp_base_dir):
    """Run timestamps should be ISO format strings."""
    storage = SQLite(base_dir=temp_base_dir)

    await storage.start_run("test", "task", ["zealot"], "human")
    await storage.complete_run("test", "success", 10)

    runs = await storage.list_runs()
    run = runs[0]

    # Should be ISO format
    assert "T" in run["started_at"]  # ISO datetime has T
    assert "T" in run["completed_at"]
