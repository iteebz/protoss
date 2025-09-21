# Protoss

**Constitutional governance for AI swarms. Self-governing telepathic alien civilization for complex coordination.**

## Quick Start

**Install:**
```bash
pip install protoss
```

**Basic Usage:**
```python
from protoss import Protoss, Config

# Initialize coordination system
protoss = Protoss(Config(agents=5, debug=True))

# Execute coordination task
result = await protoss("implement JWT authentication")
print(result)  # "Direct coordination completed: implement JWT authentication (agents: 5)"
```

**Agent-Level Usage:**
```python
from protoss.core import Bus, Config
from protoss.agents import Zealot, Archon, Conclave

# Initialize coordination infrastructure
config = Config()
bus = Bus()
await bus.start()

# Create constitutional agents
zealot = Zealot()
archon = Archon()  
conclave = Conclave("tassadar")  # Strategic perspective

# Coordinate on task
channel_id = "auth-implementation"
task = "implement JWT authentication"

await zealot.coordinate(task, channel_id, config, bus)
```

**CLI Interface:**
```bash
# Current commands
protoss coordinate "build REST API" --agents 5
protoss status
protoss config
```

## Core Principles

Protoss is built on three core principles that differentiate it from traditional multi-agent systems:

- **Constitutional Governance**: Agents are guided by distinct identities and roles, creating a system of natural checks and balances. This prevents groupthink and enhances collective intelligence by embedding a purpose-driven philosophy into each agent.

- **Emergent Coordination**: Complex workflows and team structures arise naturally from conversation (`@mentions`) rather than being dictated by rigid, top-down orchestration. The system adapts to the task, allowing for flexible and intelligent problem-solving.

- **Cognitive Sovereignty**: Agents possess autonomy over their own cognitive processes. They choose when to synchronize with the team, allowing for uninterrupted periods of "thought" and protecting against the "notification tyranny" that degrades reasoning in other systems.

## Core Architecture

**Infrastructure:** (See [Architecture](docs/ARCHITECTURE.md) for details)
- **Bus** - Message routing and coordination
- **Server** - WebSocket communication
- **Gateway** - Agent spawning and lifecycle

**Constitutional Agents:** (See [Architecture](docs/ARCHITECTURE.md) for details)
- **Zealot** - Task execution
- **Archon** - Knowledge management
- **Conclave** - Strategic consultation

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

**✅ Current (v0.1):**
- Message Bus coordination infrastructure (Bus, Server)
- Constitutional agents (Zealot, Archon, Conclave)  
- Channel-based coordination with Message protocol
- Explicit dependency injection architecture
- CLI interface with basic coordination commands

**🔄 In Development:**
- Real-time monitoring and conversational interface
- Multi-agent coordination protocols
- Advanced gateway spawning and lifecycle management

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - Current implementation patterns and essential coordination insights
- **[Vision](docs/VISION.md)** - Research question and recursive improvement vision
- **[Roadmap](docs/ROADMAP.md)** - Implementation priorities and architectural decisions
- **[Interface Design](docs/interface.md)** - UX/DX requirements and executor architecture
- **[Coordination Patterns](docs/coordination.md)** - Essential multi-agent coordination insights

⚔️ *En taro Adun*

---
*Built by Tyson Chan - tyson.chan@proton.me*