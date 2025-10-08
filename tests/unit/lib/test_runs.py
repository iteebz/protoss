"""Tests for run tracking."""

import sqlite3


from src.protoss.lib.storage import DB
from src.protoss.lib import runs


def test_shared_db_schemas(tmp_path):
    """Verify ledger and runs tables coexist in store.db."""
    base = str(tmp_path)
    db_path = tmp_path / ".protoss" / "store.db"

    conn = DB.connect(base)
    conn.close()

    old_db = runs.DB
    runs.DB = db_path
    runs.init()
    runs.DB = old_db

    with sqlite3.connect(db_path) as c:
        tables = c.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        assert ("runs",) in tables


def test_run_lifecycle(tmp_path):
    """Verify run start/complete cycle."""
    db_path = tmp_path / ".protoss" / "store.db"

    old_db = runs.DB
    runs.DB = db_path
    runs.init()

    runs.start("test-run", "test task", ["agent1", "agent2"], "test-channel")

    run_list = runs.list_runs()
    assert len(run_list) == 1
    assert run_list[0].id == "test-run"
    assert run_list[0].task == "test task"
    assert run_list[0].agents == "agent1,agent2"
    assert run_list[0].completed_at is None

    runs.complete("test-run", "success", 42)

    run_list = runs.list_runs()
    assert run_list[0].completed_at is not None
    assert run_list[0].outcome == "success"
    assert run_list[0].message_count == 42

    runs.DB = old_db
