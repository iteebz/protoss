# Archon: Context Steward

**Pathway seeding and knowledge compression for zealot coordination.**

## Core Pattern

**Archons are context stewards, not reactive services.**

```
Archon seeds pathway → Zealots coordinate in rich context → Archon compresses to archives
```

**Mental model for zealots:** Archon is helpful teammate with institutional memory, not a service to summon.

## Seeding Protocol

**Rich context injection at pathway start:**

```python
await gateway.warp_with_context(
    "Implement JWT authentication",
    keywords=["auth", "jwt", "tokens"]
)
```

**Zealots spawn into:**
- Relevant archives from previous work
- Key codebase file pointers
- Architectural constraints and decisions
- Natural coordination workflow guidance

**No empty pathways. No starting from zero.**

## Natural @archon Interaction

**Zealots ask for additional context naturally:**

```
Zealot: "@archon what about password reset patterns?"
Archon: "No archives on that yet - first implementation. Suggest following existing email patterns in notifications/"

Zealot: "@archon context on session management decisions?"  
Archon: "Previous discussion in archives/auth-session-2024.md - team chose Redis over DB for performance..."
```

**Honest responses:** 
- Found relevant context → Share it
- No archives exist → "No archives on that yet, suggest exploring codebase"
- Helpful teammate, not omniscient oracle

## Compression Protocol

**Ongoing archive maintenance:**
- Archon monitors pathway for key decisions
- Updates archives with architectural choices
- Maintains clean knowledge organization

**End-of-task compression:**
- Extract final insights and implementation summary
- Create comprehensive archive entry
- Bridge to future coordination efforts

**Knowledge accumulates organically through actual usage.**

## Architecture Benefits

**Context Continuity:**
- Future pathways start with relevant context
- Institutional memory preserved across agent spawns
- Natural knowledge evolution without artificial taxonomies

**Cognitive Relief:**
- Zealots focus on coordination and implementation
- No summoning decisions or service complexity
- Rich context eliminates "cold start" problems

**Fault Tolerance:**
- Archives provide coordination continuity
- Knowledge survives individual agent lifecycles
- Graceful degradation when archives incomplete

## Implementation

**Gateway Integration:**
```python
# Standard coordination (empty pathway)
await gateway.warp(task, agent_count)

# Context-seeded coordination (rich pathway)
await gateway.warp_with_context(task, agent_count, keywords=["auth", "jwt"])
```

**Archon Methods:**
- `seed_pathway()` - Rich context injection
- `respond_to_mention()` - @archon natural interaction  
- `compress_pathway()` - Archive maintenance

**Archives Structure:**
```
archives/
├── pathways/     # Coordination summaries
├── decisions/    # Architectural choices
├── patterns/     # Recurring solutions
└── context/      # Rich context seeds
```

## Quality Standards

**Constitutional Alignment:**
- Simple, elegant abstractions
- No enterprise complexity
- Natural emergence over imposed structure
- Agent experience first

**Practical Elegance:**
- Solves real coordination problems
- Respects agent attention architecture
- Enables month-level autonomous coordination
- Knowledge work feels natural, not ceremonial

---

*"Sometimes the most helpful thing an archon can do is say 'no archives on that yet' and let zealots explore fresh territory."*

**EN TARO ADUN.**