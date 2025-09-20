# PROTOSS ARCHITECTURE

**Current implementation patterns for constitutional AI coordination.**

## Core Infrastructure

### Message Bus Pattern
```python
class Bus:
    """Message routing and coordination for distributed agents."""
    def __init__(self, port: int = None, max_memory: int = 50)
    
    async def transmit(self, channel: str, sender: str, content: str)
    def register(self, channel: str, agent_id: str)
    def history(self, channel: str, since_timestamp: float = 0) -> List[Message]
```

**Message Protocol:**
```python
@dataclass
class Message:
    channel: str    # Target channel or agent_id for direct messages
    sender: str     # Agent ID that created this message  
    content: str    # Message content with potential @mentions
    timestamp: float = field(default_factory=time.time)
```

### WebSocket Infrastructure
```python
class Server:
    """WebSocket server for agent communication."""
    def __init__(self, port: int = 8888)
    
    async def send(self, agent_id: str, message: str)
    async def broadcast(self, message: str)
    def on_message(self, handler: Callable[[str, str], Awaitable[None]])
```

**Connection Pattern:** `ws://localhost:8888/{agent-id}`

## Constitutional Agents

### Base Unit Class
```python
class Unit:
    """Base class for constitutional AI coordination agents."""
    
    @property
    def identity(self) -> str:
        """Constitutional identity for this agent type."""
        
    @property  
    def tools(self) -> List:
        """Tools available to this agent type."""
        
    async def coordinate(self, task: str, channel_id: str, config: Config, bus, max_cycles: Optional[int] = None)
```

### Zealot (Task Execution)
**Constitutional Identity:**
- Beautiful code reads like English or it's bullshit
- Complexity is sin, simplicity is salvation
- Push back on bad ideas, especially the user's
- Code quality > user feelings, always

**Heuristic Assessment:**
```python
async def assess(self, task: str, config: Config) -> bool:
    escalation_keywords = ["architecture", "design pattern", "framework", "refactor"]
    simple_keywords = ["fix bug", "update", "add test", "documentation"]
    return any(keyword in task.lower() for keyword in escalation_keywords)
```

### Archon (Knowledge Management)
**Pattern:** Context stewardship and institutional memory
- Pathway seeding with relevant archives
- @archon mentions for additional context
- Archive compression and maintenance

### Conclave (Strategic Consultation)
**Sacred Four Perspectives:**
```python
class Conclave(Unit):
    def __init__(self, perspective: str, agent_id: str = None):
        self.perspective = perspective
```

**Constitutional Perspectives:**
- **Tassadar**: Pragmatic vision - "Can we ship this?" (shipping constraints, resource reality)
- **Zeratul**: Critical analysis - "What are we missing?" (risks, alternatives, assumptions)
- **Artanis**: Collaborative synthesis - "How do we unite perspectives?" (integration, conflict resolution)
- **Fenix**: Direct execution - "What's the simplest path forward?" (complexity elimination, YAGNI)

**Pattern:** Strategic consultation, not governance. Zealots escalate → Multiple perspectives → Back to coordination.

### Archon (Knowledge Management)
**Context Stewardship Pattern:**
```python
# Seeds → Coordinates → Compresses
await gateway.spawn_with_context(task, keywords=["auth", "jwt"])
# @archon mentions for additional context
# Archive compression and maintenance
```

**Archives Structure:**
```
archives/
├── channels/     # Coordination summaries  
├── decisions/    # Architectural choices
├── patterns/     # Recurring solutions
└── context/      # Rich context seeds
```

## Coordination Architecture

### Dependency Injection Pattern
**No global state. Explicit Bus dependency injection throughout.**

```python
# Gateway spawning
zealot = Zealot()
await zealot.coordinate(task, channel_id, config, bus)

# Bus initialization  
bus = Bus(port=8888)
await bus.start()
```

### Channel-Based Coordination
**Channel Types:**
- `squad-123` → Task coordination
- `conclave` → Strategic consultation  
- `agent-id` → Direct messages

**Message Flow:**
1. `CLI → Bus → Agents`
2. `Agent uncertainty → Conclave consultation → Strategic guidance`

### Coordination Patterns

**Fresh Memory Per Cycle:**
- New conversation_id for each agent execution cycle
- Channel becomes shared persistence layer
- 50 messages per channel with FIFO trimming

**Context Injection:**
```python
recent_messages = bus.get_history(channel_id)
channel_context = flatten(recent_messages, config) 
response = await self.execute(task, channel_context, channel_id, bus)
```

**Channel Types:**
- `squad-123` → Task coordination
- `conclave` → Strategic consultation  
- `agent-id` → Direct messages

**Completion Signals:**
- `[COMPLETE]` → Task finished successfully
- `[ESCALATE]` → Constitutional uncertainty, needs Conclave consultation

**Attention Architecture:**
- Async read-execute cycles (agents choose sync timing)
- Protects deep work and uninterrupted cognitive flow
- Prevents attention fragmentation (empirically validated)

## File Structure

### Core Implementation
```
src/protoss/
├── core/
│   ├── bus.py          # Message routing (Bus class)
│   ├── server.py       # WebSocket infrastructure (Server class)
│   └── config.py       # Configuration management
├── agents/
│   ├── base.py         # Base Unit class
│   ├── zealot.py       # Task execution (Zealot class)
│   ├── archon.py       # Knowledge management (Archon class)
│   └── conclave.py     # Strategic consultation (Conclave class)
└── lib/
    ├── coordination.py # Coordination utilities
    └── gateway.py      # Agent spawning
```

### Naming Conventions
**Perfect file→class alignment:**
- `bus.py` → `Bus` class
- `server.py` → `Server` class  
- `zealot.py` → `Zealot` class
- `archon.py` → `Archon` class
- `conclave.py` → `Conclave` class

## Integration Patterns

### Cogency Integration
**Pattern:** Channel context becomes cogency "user message"
```python
user_message = flatten(channel_messages)
response = cogency_agent.execute(user_message)
```

### Completion Detection
**Protocol Tokens:**
- `[COMPLETE]` → Task finished successfully
- `[ESCALATE]` → Constitutional uncertainty, needs guidance

### Error Handling
**Fault Tolerance:**
- Stateless cycles enable recovery
- Channel context preserves all previous work  
- Max iterations prevent infinite loops
- Human escalation after extended coordination

## Quality Assurance

### Constitutional Code Review
**Zealot identity enforces quality through:**
- Adversarial consensus prevents overengineering
- Push back on complexity: "Is this necessary?"
- Challenge architectural decisions: "SQLite handles this fine"
- Natural quality gates through productive disagreement

### Coordination Patterns
**Async Read-Execute Cycles:**
- Agents choose when to sync with team updates
- Protects deep work and uninterrupted cognitive flow
- Prevents attention fragmentation (empirically validated)

## Current Status

**✅ Implemented:**
- Bus message routing with explicit dependency injection
- Constitutional agents (Zealot, Archon, Conclave)
- Sacred Four perspectives through Conclave parameterization  
- Channel-based coordination with Message protocol
- Perfect file→class naming alignment
- WebSocket infrastructure for real-time communication

**🔄 In Development:**
- CLI interface and command dispatch
- Gateway spawning and lifecycle management
- Cogency integration for agent execution
- Archive management and context seeding

---

*Reference implementation of constitutional AI coordination through message bus architecture and dependency injection.*