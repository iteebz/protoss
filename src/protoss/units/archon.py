"""Institutional memory for Protoss swarm."""

import asyncio
import json
import sqlite3
import time
from pathlib import Path
from typing import Optional

from ..structures.pylon import Psi


class Archon:
    """Institutional memory for Protoss swarm coordination."""
    
    def __init__(self, protoss_dir: Path = None):
        """Initialize Archon with storage paths."""
        self.protoss_dir = protoss_dir or Path(".protoss")
        self.protoss_dir.mkdir(exist_ok=True)
        self.knowledge_dir = self.protoss_dir / "knowledge"
        self.knowledge_dir.mkdir(exist_ok=True)
        self.db_path = self.protoss_dir / "protoss.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize task tracking database."""
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zealot_id TEXT NOT NULL,
                    task TEXT NOT NULL,
                    result TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            db.commit()
    
    async def log_task(self, zealot_id: str, task: str, result: str, success: bool):
        """Log task execution for tracking."""
        with sqlite3.connect(self.db_path) as db:
            db.execute(
                "INSERT INTO tasks (zealot_id, task, result, success, timestamp) VALUES (?, ?, ?, ?, ?)",
                (zealot_id, task, result, success, time.time())
            )
            db.commit()
    
    async def learn_pattern(self, domain: str, insight: str):
        """Store coordination wisdom in domain-specific markdown."""
        domain_file = self.knowledge_dir / f"{domain}.md"
        
        # Create domain file if it doesn't exist
        if not domain_file.exists():
            content = f"# {domain.title()}\n\nCoordination wisdom for {domain}.\n\n"
        else:
            with open(domain_file, 'r') as f:
                content = f.read()
        
        # Append new insight with timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M")
        content += f"\n## {timestamp}\n{insight}\n"
        
        with open(domain_file, 'w') as f:
            f.write(content)
    
    async def query_knowledge(self, domain: str) -> str:
        """Query domain-specific wisdom."""
        domain_file = self.knowledge_dir / f"{domain}.md"
        
        if not domain_file.exists():
            return f"No wisdom recorded for {domain}"
        
        with open(domain_file, 'r') as f:
            return f.read()
    
    async def process_psi_message(self, message: Psi):
        """Process PSI message for learning opportunities."""
        await self._extract_wisdom(message)
    
    async def _extract_wisdom(self, message: Psi):
        """Extract coordination wisdom from significant messages."""
        # Just use the message type as domain
        domain = message.type.lower()
        await self.learn_pattern(domain, f"From {message.source}: {message.content}")