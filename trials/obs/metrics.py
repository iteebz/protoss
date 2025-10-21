#!/usr/bin/env python3
"""Trial metrics analyzer."""

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path


def get_metrics(trial_path: str) -> dict:
    """Calculate aggregate metrics for trial."""
    ledger = Path(trial_path) / "ledger.db"
    if not ledger.exists():
        return {}

    conn = sqlite3.connect(ledger)
    conn.row_factory = sqlite3.Row

    # Messages per channel
    channel_counts = {}
    rows = conn.execute(
        "SELECT channel, COUNT(*) as count FROM ledger GROUP BY channel"
    ).fetchall()
    for row in rows:
        channel_counts[row["channel"]] = row["count"]

    # Messages per agent per channel
    agent_counts = defaultdict(lambda: defaultdict(int))
    rows = conn.execute(
        "SELECT channel, sender, COUNT(*) as count FROM ledger GROUP BY channel, sender"
    ).fetchall()
    for row in rows:
        agent_counts[row["channel"]][row["sender"]] = row["count"]

    # Spawn events (legacy ledgers may omit parent column)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(ledger)").fetchall()}
    if "parent" in columns:
        spawn_count = conn.execute(
            "SELECT COUNT(DISTINCT channel) FROM ledger WHERE parent IS NOT NULL"
        ).fetchone()[0]
    else:
        spawn_count = 0

    # Completion signals
    completion_count = conn.execute(
        "SELECT COUNT(*) FROM ledger WHERE content LIKE '%!complete%'"
    ).fetchone()[0]

    # Despawn signals
    despawn_count = conn.execute(
        "SELECT COUNT(*) FROM ledger WHERE content LIKE '%!despawn%'"
    ).fetchone()[0]

    # Total messages
    total_messages = conn.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]

    # Unique channels
    unique_channels = conn.execute(
        "SELECT COUNT(DISTINCT channel) FROM ledger"
    ).fetchone()[0]

    conn.close()

    return {
        "total_messages": total_messages,
        "unique_channels": unique_channels,
        "spawn_count": spawn_count,
        "completion_signals": completion_count,
        "despawn_signals": despawn_count,
        "messages_per_channel": channel_counts,
        "agent_participation": dict(agent_counts),
    }


def print_metrics(metrics: dict):
    """Print metrics in readable format."""
    print(f"Total messages: {metrics['total_messages']}")
    print(f"Unique channels: {metrics['unique_channels']}")
    print(f"Spawned channels: {metrics['spawn_count']}")
    print(f"Completion signals: {metrics['completion_signals']}")
    print(f"Despawn signals: {metrics['despawn_signals']}")
    print()

    print("Messages per channel:")
    for channel, count in metrics["messages_per_channel"].items():
        print(f"  #{channel}: {count}")
    print()

    print("Agent participation:")
    for channel, agents in metrics["agent_participation"].items():
        print(f"  #{channel}:")
        for agent, count in agents.items():
            print(f"    {agent}: {count}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m obs.metrics <trial_path> [--json]")
        sys.exit(1)

    trial_path = sys.argv[1]
    metrics = get_metrics(trial_path)

    if "--json" in sys.argv:
        print(json.dumps(metrics, indent=2))
    else:
        print_metrics(metrics)
