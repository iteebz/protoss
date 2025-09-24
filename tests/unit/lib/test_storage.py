"""SQLite storage tests."""

import pytest
import pytest_asyncio

from protoss.lib.storage import SQLite


@pytest_asyncio.fixture
async def storage(tmp_path):
    db_path = tmp_path / "events.db"
    store = SQLite(db_path=str(db_path))
    await store._init_db()
    return store


@pytest.mark.asyncio
async def test_save_and_load(storage: SQLite):
    event = {
        "type": "agent_message",
        "channel": "alpha",
        "sender": "zealot",
        "timestamp": 100.0,
        "payload": {"content": "hi"},
    }

    await storage.save_event(event)
    loaded = await storage.load_events(channel="alpha")

    assert len(loaded) == 1
    assert loaded[0]["payload"]["content"] == "hi"


@pytest.mark.asyncio
async def test_load_events_with_filters(storage: SQLite):
    events = [
        {
            "type": "agent_message",
            "channel": "alpha",
            "sender": "zealot",
            "timestamp": 100.0,
            "payload": {"content": "one"},
        },
        {
            "type": "agent_message",
            "channel": "alpha",
            "sender": "archon",
            "timestamp": 200.0,
            "payload": {"content": "two"},
        },
        {
            "type": "agent_message",
            "channel": "beta",
            "sender": "probe",
            "timestamp": 300.0,
            "payload": {"content": "three"},
        },
    ]

    for event in events:
        await storage.save_event(event)

    alpha = await storage.load_events(channel="alpha")
    assert len(alpha) == 2

    alpha_recent = await storage.load_events(channel="alpha", since=150)
    assert len(alpha_recent) == 1
    assert alpha_recent[0]["payload"]["content"] == "two"
