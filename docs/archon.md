# Archon

Knowledge synthesis and institutional memory for Protoss coordination.

## Architecture
```
.protoss/
├── knowledge/      # Coordination wisdom (markdown)
└── protoss.db      # Task tracking (SQLite)
```

## Interface
```python
class Archon:
    async def synthesize_research(self, zealot_results: List[str]) -> str
    async def log_task(self, zealot_id: str, task: str, result: str, success: bool)
    async def learn_pattern(self, domain: str, insight: str)  
    async def query_knowledge(self, domain: str) -> str
    async def process_psi_message(self, message: Psi)
```

## Core Functions
- **Research synthesis**: Distills parallel Zealot threads into coherent insights
- **Task logging**: Tracks execution patterns across swarm coordination  
- **Pattern extraction**: Identifies coordination wisdom from successful/failed attempts
- **Institutional memory**: Preserves learning across sessions and agent lifecycles

## Storage Architecture
- **Tasks** → SQLite (structured execution tracking)
- **Synthesis** → `knowledge/{domain}.md` (human-readable insights)
- **Patterns** → Git-trackable markdown for institutional learning

Knowledge domains emerge organically from coordination patterns. No predefined categories.