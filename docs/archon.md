# Archon

Institutional memory for Protoss swarm.

## Architecture
```
.protoss/
├── knowledge/      # Coordination wisdom (markdown)
└── protoss.db      # Task tracking (SQLite)
```

## Interface
```python
class Archon:
    async def log_task(self, zealot_id: str, task: str, result: str, success: bool)
    async def learn_pattern(self, domain: str, insight: str)  
    async def query_knowledge(self, domain: str) -> str
    async def process_psi_message(self, message: Psi)
```

## Message Integration
Archon processes §PSI messages via Pylon. Logs all tasks. Extracts wisdom from significant events only.

## Storage
- **Tasks** → `.db` (structured queries)
- **Wisdom** → `knowledge/{domain}.md` (human-readable, git-trackable)

Knowledge domains emerge from usage patterns. No predefined categories.