# PROTOSS ARCHITECTURE

**Implementation reference for constitutional AI coordination.**

## Core Architecture Patterns

### Agent Communication
**Built on cogency streaming patterns**

- Agents use cogency's natural `§respond:` and `§end` delimiters
- Fresh conversation_id per cycle prevents context explosion
- Channel becomes shared persistence layer

### Adaptive Spawning Architecture  
**Conversational agent summoning through @mentions**

- Agent writes `§respond: Need @zealot help`
- Bus detects @mentions and spawns agents conversationally
- Universal `bus.spawn()` API for fresh or reactivate semantics
- Agents self-manage lifecycle with `!despawn`

**→ See [coordination.md](coordination.md) for adaptive spawning implementation**

### Constitutional Deliberation
**Strategic consultation through Sacred Four Perspectives**

- Zealots escalate complex decisions with `@conclave`
- Conclave provides diverse strategic perspectives (Tassadar, Zeratul, Artanis, Fenix)  
- Strategic consultation, not governance
- Natural quality gates through constitutional disagreement

**→ See [deliberation.md](deliberation.md) for complete conclave patterns**

### Institutional Knowledge Management
**Context stewardship and pathway seeding**

- Archons seed pathways with relevant context (no empty starts)
- Natural @archon mentions for institutional memory access
- Archive compression after coordination completion
- Agent-specific context filtering (archons see full audit trail)

**→ See [knowledge.md](knowledge.md) for complete archon patterns**

### Human Interface Integration
**Bidirectional constitutional translation**

- @arbiter for context compression and human voice relay
- Constitutional pushback capability on human directives
- Two modes: passive monitoring and active conversation
- Human-swarm coordination without micromanagement

**→ See [interface.md](interface.md) for complete human interface patterns**

## Core Infrastructure

### Bus with Spawner Integration
**Message routing with adaptive agent lifecycle management**

```python
# Universal agent participation API
await bus.spawn("zealot", channel_id)           # Fresh agent
await bus.spawn("zealot-abc123", channel_id)    # Reactivate specific
await bus.despawn(agent_id)                     # Agent removal
```

**Clean Semantics:**
- `bus.spawn()` → Universal agent participation (fresh or reactivate)
- `bus.despawn()` → Agent removal from coordination
- Agents self-manage with `!despawn` command
- Persistent by default → SQLite-backed history keeps channel transcripts across restarts (override `enable_storage=False` for ephemeral tests)

### Constitutional Agent Framework
**Base class for constitutional AI coordination**

```python
class Unit:
    @property
    def identity(self) -> str:
        """Constitutional identity for this agent type."""
        
    async def execute(self, task: str, channel_context: str, channel_id: str, bus) -> str:
        """Single execution cycle with streaming protocol."""
        
    async def coordinate(self, task: str, channel_id: str, config: Config, bus) -> str:
        """Coordination loop with lifecycle signal detection."""
```

### Constitutional Agent Types

**Zealot** → Task execution with architectural criticism  
**Archon** → Institutional memory and context stewardship  
**Conclave** → Strategic consultation through Sacred Four Perspectives  
**Arbiter** → Human interface with bidirectional translation  

**→ See individual docs for detailed constitutional identities and patterns**

## Coordination Command Protocol

**@ = Participation Control** → Summon agents (`@zealot`, `@archon-abc123`)  
**Natural Names = Communication** → Talk to active agents (`zealot-abc123, thoughts?`)  
**! = Self-Action** → Individual lifecycle management (`!despawn`)

## File Structure

### Implementation Structure
```
src/protoss/
├── core/
│   ├── bus.py          # Message routing with spawner integration
│   ├── spawner.py      # Adaptive agent spawning and lifecycle  
│   ├── server.py       # WebSocket infrastructure
│   ├── message.py      # Message protocol with @mention detection
│   ├── config.py       # Configuration management
│   └── coordination.py # Context filtering and signal parsing
├── agents/
│   ├── base.py         # Base Unit with streaming protocol
│   ├── zealot.py       # Task execution agent
│   ├── archon.py       # Knowledge management agent
│   ├── conclave.py     # Strategic consultation agent
│   └── arbiter.py      # Human interface agent
└── engine.py           # Main coordination engine
```

### Integration Patterns

**Cogency Integration:** Channel context → cogency user message → streaming events → bus transmission  
**Lifecycle Signal Detection:** `[COMPLETE]`, `@conclave`, `!despawn`, `!despawn` parsing  
**WebSocket Infrastructure:** Real-time coordination network with dependency injection  

**→ See implementation files for detailed integration patterns**

## Documentation Architecture

**[coordination.md](coordination.md)** → Core coordination breakthrough patterns  
**[deliberation.md](deliberation.md)** → Sacred Four strategic consultation  
**[knowledge.md](knowledge.md)** → Archon context stewardship and archives  
**[interface.md](interface.md)** → Human-swarm bidirectional interface  

## Core Insights

**Fresh Memory + Channel Persistence:**
- New conversation_id prevents cogency context explosion
- Channel becomes shared team memory layer
- Agents get fresh cognitive perspective each cycle

**Conversational Coordination:**
- No hardcoded workflows or orchestration
- Pure emergence through constitutional conversation
- @mentions create adaptive team formation

**Constitutional Quality Assurance:**
- Agent identities create productive disagreement
- Natural quality gates through constitutional tension
- Human interface preserves agent autonomy

**Agent Experience First:**
- Streaming protocol respects agent cognition
- Context filtering optimizes for agent type
- Async coordination prevents attention fragmentation

---

*Implementation reference for constitutional AI coordination architecture.*
