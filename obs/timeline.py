#!/usr/bin/env python3
"""Multi-channel timeline analyzer."""

import sqlite3
import sys
from pathlib import Path


def get_timeline(trial_path: str) -> list[dict]:
    """Get all messages across all channels, sorted by timestamp."""
    ledger = Path(trial_path) / "ledger.db"
    if not ledger.exists():
        return []
    
    conn = sqlite3.connect(ledger)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute(
        "SELECT channel, sender, content, timestamp FROM ledger ORDER BY timestamp"
    ).fetchall()
    
    messages = [dict(row) for row in rows]
    conn.close()
    return messages


def print_timeline(messages: list[dict], show_channel: bool = True):
    """Print timeline in readable format."""
    for msg in messages:
        channel = f"#{msg['channel']}" if show_channel else ""
        sender = msg["sender"].upper()
        content = msg["content"][:100].replace("\n", " ")
        
        if show_channel:
            print(f"[{channel}] {sender}: {content}")
        else:
            print(f"{sender}: {content}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m obs.timeline <trial_path>")
        sys.exit(1)
    
    trial_path = sys.argv[1]
    messages = get_timeline(trial_path)
    
    show_channel = "--no-channel" not in sys.argv
    print_timeline(messages, show_channel=show_channel)
