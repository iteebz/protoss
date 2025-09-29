"""Inspection tools for querying Protoss coordination state."""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..core.config import Config


@dataclass
class CoordinationStatus:
    """Status of a coordination session."""
    coordination_id: str
    channel: str
    message_count: int
    active_agents: List[str]
    last_activity: str
    complete: bool


@dataclass 
class MessageRecord:
    """A message from the coordination history."""
    timestamp: str
    sender: str
    content: str
    message_type: str
    coordination_id: str


class ProtossInspector:
    """Synchronous inspector for Protoss coordination state."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db_path = Path.home() / ".protoss" / "bus.db"
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get SQLite connection to Protoss database."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Protoss database not found at {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def list_coordinations(self) -> List[CoordinationStatus]:
        """List all coordination sessions."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    coordination_id,
                    channel,
                    COUNT(*) as message_count,
                    MAX(timestamp) as last_activity,
                    GROUP_CONCAT(DISTINCT sender) as senders
                FROM events 
                WHERE coordination_id IS NOT NULL
                GROUP BY coordination_id, channel
                ORDER BY last_activity DESC
            """)
            
            results = []
            for row in cursor:
                senders = row["senders"].split(",") if row["senders"] else []
                active_agents = [s for s in senders if s.startswith(("arbiter-", "zealot-", "probe-"))]
                
                # Simple completion heuristic: has agent response
                complete = any(s.startswith("arbiter-") for s in senders)
                
                results.append(CoordinationStatus(
                    coordination_id=row["coordination_id"],
                    channel=row["channel"],
                    message_count=row["message_count"],
                    active_agents=active_agents,
                    last_activity=row["last_activity"],
                    complete=complete
                ))
            
            return results
    
    def get_messages(self, coordination_id: str) -> List[MessageRecord]:
        """Get all messages for a coordination session."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT timestamp, sender, content, type, coordination_id
                FROM events 
                WHERE coordination_id = ?
                ORDER BY timestamp ASC
            """, (coordination_id,))
            
            return [
                MessageRecord(
                    timestamp=row["timestamp"],
                    sender=row["sender"], 
                    content=row["content"],
                    message_type=row["type"],
                    coordination_id=row["coordination_id"]
                )
                for row in cursor
            ]
    
    def get_coordination_status(self, coordination_id: str) -> Optional[CoordinationStatus]:
        """Get status of specific coordination."""
        coordinations = self.list_coordinations()
        return next((c for c in coordinations if c.coordination_id == coordination_id), None)
    
    def is_complete(self, coordination_id: str) -> bool:
        """Check if coordination is complete."""
        status = self.get_coordination_status(coordination_id)
        return status.complete if status else False