#!/usr/bin/env python3
"""Channel spawn topology analyzer."""

import json
import sqlite3
import sys
from pathlib import Path


def get_topology(trial_path: str) -> dict:
    """Extract channel spawn topology from ledger.db."""
    ledger = Path(trial_path) / "ledger.db"
    if not ledger.exists():
        return {}
    
    conn = sqlite3.connect(ledger)
    conn.row_factory = sqlite3.Row
    
    channels = {}
    rows = conn.execute(
        "SELECT DISTINCT channel, parent FROM ledger WHERE parent IS NOT NULL"
    ).fetchall()
    
    for row in rows:
        channels[row["channel"]] = row["parent"]
    
    all_channels = conn.execute("SELECT DISTINCT channel FROM ledger").fetchall()
    for row in all_channels:
        if row["channel"] not in channels:
            channels[row["channel"]] = None
    
    conn.close()
    return channels


def build_tree(channels: dict) -> dict:
    """Build hierarchical tree from parent relationships."""
    roots = [ch for ch, parent in channels.items() if parent is None]
    
    def get_children(parent):
        return [ch for ch, p in channels.items() if p == parent]
    
    def build_node(channel):
        return {
            "channel": channel,
            "children": [build_node(child) for child in get_children(channel)]
        }
    
    return [build_node(root) for root in roots]


def print_tree(tree: list, indent: int = 0):
    """Print ASCII tree."""
    for node in tree:
        prefix = "  " * indent
        symbol = "└─" if indent > 0 else "●"
        print(f"{prefix}{symbol} #{node['channel']}")
        print_tree(node["children"], indent + 1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m obs.topology <trial_path>")
        sys.exit(1)
    
    trial_path = sys.argv[1]
    channels = get_topology(trial_path)
    tree = build_tree(channels)
    
    if "--json" in sys.argv:
        print(json.dumps(tree, indent=2))
    else:
        print_tree(tree)
