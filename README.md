# Protoss

**Constitutional governance for AI swarms. Self-governing telepathic alien civilization for complex coordination.**

Protoss is a constitutional AI coordination architecture in active development, designed for emergent intelligence in multi-agent swarms. The core infrastructure (message bus, agent lifecycle, CLI) is implemented and working, but coordination patterns are actively being refined and tested. This system explores a novel approach to scaling AI development beyond human micromanagement through constitutional governance rather than rigid orchestration.

## Quick Start

**Install:**
```bash
pip install protoss
```

**Basic Usage:**
```python
import asyncio
from protoss import Protoss

async def main():
    # Initialize coordination system with a vision
    async with Protoss("implement JWT authentication") as swarm:
        result = await swarm
        print(f"Constitutional emergence complete: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

**CLI Interface:**
```bash
# Start the Protoss Bus (unified coordination nucleus)
protoss bus

# Run a coordination task (human provides vision, agents emerge)
protoss run "build REST API"

# Check current swarm status
protoss status

# Ask the swarm a question via the Arbiter
protoss ask "should we refactor this auth system?"
```

## Core Principles

Protoss is built on three core principles that differentiate it from traditional multi-agent systems:

- **Constitutional Governance**: Agents are guided by distinct identities and roles, creating a system of natural checks and balances. This prevents groupthink and enhances collective intelligence by embedding a purpose-driven philosophy into each agent.

- **Emergent Coordination**: Complex workflows and team structures arise naturally from conversation (`@mentions`) rather than being dictated by rigid, top-down orchestration. The system adapts to the task, allowing for flexible and intelligent problem-solving.

- **Cognitive Sovereignty**: Agents possess autonomy over their own cognitive processes. They choose when to synchronize with the team, allowing for uninterrupted periods of "thought" and protecting against the "notification tyranny" that degrades reasoning in other systems.

## Core Architecture

**Infrastructure:** (See [Architecture](docs/ARCHITECTURE.md) for details)
- **Bus** - Unified coordination nucleus (message routing, agent spawning, lifecycle)
- **Server** - WebSocket communication
- **Gateway** - Pure spawning functions (stateless agent process creation)

**Constitutional Agents:** (See [Architecture](docs/ARCHITECTURE.md) for details)
- **Zealot** - Architectural criticism and code execution
- **Archon** - Institutional memory and context stewardship
- **Conclave** - Strategic consultation through Sacred Four
- **Arbiter** - Human interface and coordination translation
- **Oracle** - Prophecy and system insight

**Coordination Flow:** (See [Coordination Patterns](docs/coordination.md) for details)
**Escalation Flow:** (See [Constitutional Deliberation](docs/deliberation.md) for details)

## Research Question

**Constitutional agent swarm for complex work.** Better than Claude/Cursor/Codex through:
- Multiple constitutional perspectives preventing groupthink
- Adaptive expertise spawning via @mention protocols  
- Institutional memory across coordination sessions
- Democratic deliberation for hard problems

RSI capabilities emerge naturally from constitutional coordination, but the immediate value is **coordinated constitutional intelligence** for complex tasks humans can't handle alone.

## Implementation Status

**Working Infrastructure:**
- Message Bus coordination infrastructure (Bus, Server, Gateway)
- Constitutional agents (Zealot, Archon, Conclave, Arbiter, Oracle)
- Channel-based coordination with Message protocol
- CLI interface with basic coordination commands
- Evaluation framework for coordination testing

**Active Development:**
- Multi-agent coordination pattern validation
- Real-time monitoring and conversational interface enhancements
- Advanced emergent spawning and lifecycle management
- Constitutional governance effectiveness testing

## Documentation

**Core Architecture:**
- **[Architecture](docs/ARCHITECTURE.md)** - Current implementation patterns and essential coordination insights
- **[Vision](docs/VISION.md)** - Research question and recursive improvement vision
- **[Cathedral](docs/CATHEDRAL.md)** - Architectural breakthrough and interface poetry
- **[Roadmap](docs/ROADMAP.md)** - Implementation priorities and architectural decisions

**Design Philosophy:**
- **[Agent Experience](philosophy/ax.md)** - Agent-centric design methodology and constitutional self-design
- **[Code Philosophy](philosophy/code.md)** - Sacred craft standards and reference-grade architecture principles

**Coordination Patterns:**
- **[Coordination Blueprints](docs/blueprints/)** - Constitutional governance technical specifications
- **[Memetic Transmission](docs/memesis/)** - AI self-indoctrination and constitutional propagation protocols

⚔️ *En taro Adun*

---
*Built by Tyson Chan - tyson.chan@proton.me*