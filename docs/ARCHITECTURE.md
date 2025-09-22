# PROTOSS ARCHITECTURE

**Cathedral interface for constitutional AI coordination.**

## Core Architecture: Three Pillars

The Protoss architecture is founded upon the "Three Pillars of the Emergent Protocol," as detailed in [Emergence: The Constitutional Language of the Swarm](coordination.md). These pillars are:

1.  **Constitutional Identity over Explicit Instruction**: Agents act based on their inherent nature and channel context.
2.  **Natural Language as the Medium of Coordination**: `@mention` is the universal interface for intelligent dialogue.
3.  **Sovereignty and Agent Judgment**: Agents control their lifecycle and exercise independent judgment.

## Cathedral Interface

### Protoss: Pure Coordination Poetry
```python
# Cathedral interface - everything else is implementation
async with Protoss("build authentication system") as swarm:
    result = await swarm
```

### Bus: Unified Coordination Nucleus  
Central coordination combining message routing and agent spawning. Detects @mentions and spawns constitutional agents. Manages active agent tracking and lifecycle.

### Gateway: Pure Spawning Functions
Stateless functions for agent process creation. No state management - serves Bus spawning needs.

### Constitutional Agent Types

For detailed descriptions of each agent, refer to [Emergence: The Constitutional Language of the Swarm](coordination.md). Briefly:

-   **Zealot** → Architectural criticism and code execution
-   **Archon** → Institutional memory and context stewardship
-   **Conclave** → Strategic consultation through Sacred Four
-   **Arbiter** → Human interface and coordination translation
-   **Oracle** → Web scrape and search research

## Implementation Structure
```
src/protoss/
├── core/
│   ├── protoss.py      # Cathedral interface
│   ├── bus.py          # Unified coordination nucleus
│   ├── gateway.py      # Pure spawning functions
│   ├── server.py       # WebSocket infrastructure
│   └── message.py      # Message protocol with signal parsing
├── agents/
│   ├── unit.py         # Base agent with !despawn sovereignty
│   ├── zealot.py       # Architectural criticism agent
│   ├── archon.py       # Institutional memory agent
│   ├── conclave.py     # Strategic consultation agent
│   ├── arbiter.py      # Human interface agent
│   └── oracle.py       # System insight agent
└── cli.py              # Command-line interface
```

## Sacred Guardrails

The Protoss swarm operates with "Sacred Guardrails" as defined in [Emergence: The Constitutional Language of the Swarm](coordination.md) and further elaborated in [Constitutional Safety Principles](SAFETY.md). These include:

-   `!emergency` → Halts the entire swarm.
-   `!despawn` → Agent's sovereign act of concluding its mandate.

All other interventions are handled via natural language `@mention` dialogue.

## Constitutional Emergence

**No orchestration. No workflows. No ceremony.**

Agents coordinate through constitutional dialogue. @mentions spawn additional expertise when needed. Natural completion through constitutional wisdom.

---

*Implementation reference for constitutional AI coordination architecture.*
