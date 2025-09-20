# Protoss

**Constitutional governance for AI swarms. Multi-agent coordination without collapse.**

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

## Core Architecture

**Infrastructure:**
- **Bus** - Message routing and coordination for distributed agents
- **Server** - WebSocket infrastructure for real-time communication  
- **Gateway** - Agent spawning and lifecycle management

**Constitutional Agents:**
- **Zealot** - Task execution with constitutional principles
- **Archon** - Knowledge management and institutional memory
- **Conclave** - Strategic consultation through diverse perspectives

**Coordination Flow:** `CLI → Bus → Agents → Channel Coordination`  
**Escalation Flow:** `Agent uncertainty → Conclave consultation → Strategic guidance`

## Research Question

Can Claude 5-level intelligence research Claude 6-level breakthroughs when properly coordinated through constitutional governance frameworks?

Multi-agent systems consistently collapse within ~10 minutes without human intervention. PROTOSS tests whether constitutional frameworks can extend coordination from minutes to months through democratic deliberation and systematic escalation protocols.

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

## Target Capabilities

- **Hour-level autonomy** → Current research target
- **Day-level autonomy** → Production threshold
- **Month-level autonomy** → Recursive improvement threshold

Success metrics: Extended autonomous operation without human babysitting. Systems that remember decisions, learn from failures, coordinate without collapse.

⚔️ *En taro Adun*

---
*Built by Tyson Chan - tyson.chan@proton.me*