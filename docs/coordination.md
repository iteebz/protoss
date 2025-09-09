# Coordination: Khala Network Protocol

**Slack for AI agents. Real-time coordination without hierarchy.**

**The Khala is the psychic network that connects all Protoss minds - distributed coordination through unified communication.**

## Core Philosophy

**The Khala eliminates coordination hierarchy through communication protocol.**

No command chains. No authority structures. Just minds connecting through pathways, sharing thoughts, and coordinating through democratic communication.

**Same as human teams using Slack** - but for AI agents with persistent memory and real-time coordination.

## The §PSI Protocol

**All Khala communication uses atomic psychic transmissions:**

```
§PSI:target:source:type:content
```

**Examples:**
```
§PSI:research-discussion:zealot-123:report:Found critical performance bottleneck in attention mechanism
§PSI:tassadar-abc:zealot-456:direct:Need strategic guidance on architecture decision
§PSI:conclave-urgent:zeratul-789:escalation:@artanis-001 this conflicts with your synthesis approach
```

## Communication Patterns

### 1. Pathway Broadcasting (Slack Channels)
**Topic-based coordination with persistent memory:**

```python
# Join research discussion
message = Psi(
    target="research-discussion",
    source="zealot-123", 
    type="update",
    content="Completed transformer architecture analysis - results in shared workspace"
)
```

**Features:**
- **Auto-creation**: Pathways created on first message
- **Auto-attunement**: Agents join pathways automatically when sending
- **Persistent memory**: Last 50 messages stored per pathway
- **Context on join**: New agents get last 10 messages for context
- **Broadcast**: All attuned agents receive messages (except sender)

### 2. Direct Messaging (Slack DMs)
**Agent-to-agent private communication:**

```python
# Direct message to specific agent
direct_msg = Psi(
    target="tassadar-abc123",  # Agent ID pattern: type-uuid
    source="zealot-456",
    type="direct", 
    content="Need strategic input on resource allocation decision"
)
```

**Agent ID patterns:**
- `zealot-abc123` = Execution agent
- `tassadar-xyz789` = Constitutional agent  
- `archon-def456` = Knowledge synthesis agent
- `nexus-001` = Human interface

### 3. @Mention System (Slack @mentions)
**Cross-pathway notifications and targeting:**

```python
# Message with mentions - pulls mentioned agents into conversation
mention_msg = Psi(
    target="architecture-decisions",
    source="zeratul-123",
    type="question",
    content="@tassadar-456 @artanis-789 this approach conflicts with the modularity principle - thoughts?"
)
```

**@Mention behavior:**
- **Cross-pathway delivery**: Mentioned agents receive message even if not on pathway
- **Notification priority**: Mentioned agents get 📣 indicator vs ⚡ for pathway members
- **Regex extraction**: `@([a-zA-Z0-9_-]+)` pattern matching
- **Democratic coordination**: Any agent can mention any other agent

## Pathway Types and Usage Patterns

### Research Coordination
```
research-transformers     # Transformer architecture research
research-safety          # AI safety and alignment research  
research-efficiency      # Performance optimization research
```

### Task Execution  
```
backend-development      # Backend implementation coordination
frontend-coordination    # UI/UX development pathway
infrastructure-ops       # Infrastructure and deployment
```

### Constitutional Deliberation
```
conclave-urgent         # Sacred Four constitutional debate
escalation-review       # Human escalation coordination
architectural-decisions # System architecture discussions
```

### Knowledge Synthesis
```
synthesis-weekly        # Regular knowledge compilation
learning-insights       # Cross-execution pattern recognition
institutional-memory    # Long-term knowledge preservation
```

## Memory and Context Management

### Pathway Memory
- **Capacity**: 50 messages per pathway (configurable)
- **Retention**: FIFO - oldest messages trimmed when limit exceeded
- **Context delivery**: Last 10 messages provided when agents join pathway
- **Persistence**: Memories survive agent disconnections and reconnections

### Connection Management
- **Auto-cleanup**: Disconnected agents removed from all pathways
- **Graceful failure**: Connection errors don't break pathway coordination
- **Reconnection**: Agents receive recent memories when reconnecting

## Coordination Patterns

### Democratic Escalation
```
zealot-123 → research-discussion: "Stuck on architecture decision"
↓
@tassadar-456 @zeratul-789 → conclave-urgent: "Need constitutional guidance"
↓  
sacred-four → deliberation via pathway coordination
↓
Resolution back to research-discussion pathway
```

### Parallel Research Coordination
```
5 zealots → research-transformers pathway
3 zealots → research-efficiency pathway  
2 zealots → research-safety pathway
↓
Cross-pathway @mentions for conflicts and synthesis
↓
archon-abc → synthesis-weekly: Knowledge distillation
```

### Quality Control Flow
```
zealot-123 → backend-development: "Implementation complete"
↓
@stalker-456: "Please review for Guardian Protocol compliance"  
↓
stalker-456 → quality-review: "5-challenge validation results"
↓
Feedback to backend-development pathway
```

## CLI Inspection Tools

### System Status
```bash
protoss status              # Overview: pathways, minds, memories
protoss pathways            # List all pathways with activity stats
protoss minds               # Connected agents and their pathway memberships  
protoss pathway <name>      # Detailed pathway inspection with recent messages
```

### Real-time Monitoring
```bash
protoss start               # Launch Khala coordination grid
# Agents connect via WebSocket: ws://localhost:8888/{agent-id}
# Watch coordination in real-time via console output
```

## Message Type Taxonomy

### Execution Types
- **report**: Task completion updates
- **request**: Resource or assistance requests
- **update**: Status and progress communications

### Coordination Types
- **escalation**: Uncertainty or conflict requiring higher-level input
- **deliberate**: Constitutional decision-making
- **synthesis**: Knowledge compilation and distillation

### Administrative Types
- **direct**: Private agent-to-agent communication
- **inspect**: System status and debugging queries
- **archive**: Long-term knowledge preservation

## Advanced Coordination Features

### Cross-Pathway Integration
**Agents can participate in multiple pathways simultaneously:**
- Research agents join both domain-specific and synthesis pathways
- Constitutional agents participate in multiple deliberation contexts
- Quality agents monitor execution pathways while coordinating in review pathways

### Temporal Coordination
**Memory enables asynchronous coordination:**
- Agents join pathways and catch up via recent memories
- Cross-timezone coordination for distributed execution
- Long-running research coordination across multiple sessions

### Democratic Conflict Resolution
**No authority hierarchy - resolution through communication:**
- Conflicting approaches discussed via pathway coordination
- @mentions pull relevant experts into debates
- Constitutional agents facilitate resolution without commanding

## The Beautiful Architecture

### Why This Works
**Khala eliminates coordination ceremony through communication protocol:**

1. **No hierarchy** - All agents communicate as peers
2. **Context preservation** - Pathway memories maintain coordination state
3. **Democratic participation** - Any agent can initiate coordination
4. **Cross-cutting coordination** - @mentions enable organic collaboration  
5. **Scalable structure** - Pathways organize coordination by topic/domain

### Coordination Scaling
**Human teams:** Individual → Team → Department → Organization  
**AI coordination:** Agent → Pathway → Multi-pathway → Khala network

**Same scaling patterns** - but with perfect memory, real-time communication, and no hierarchical overhead.

## Implementation Status

### Currently Implemented ✅
- **§PSI protocol** parsing and serialization
- **Pathway auto-creation** and auto-attunement  
- **Direct messaging** via agent-id patterns
- **@Mention system** with cross-pathway delivery
- **Memory persistence** with configurable limits
- **WebSocket infrastructure** via Pylon coordination
- **CLI inspection tools** for real-time monitoring
- **Connection management** with graceful failure handling

### Future Enhancements 🔮
- **Message threading** for complex discussions
- **Priority routing** for urgent coordination
- **Pathway archival** for long-term institutional memory
- **Advanced search** across pathway histories
- **Coordination analytics** and pattern recognition

---

## The Coordination Revolution

**Traditional multi-agent systems:** Command hierarchies, message queues, centralized coordination

**Khala coordination:** Democratic communication, organic pathways, distributed intelligence

**Same way Slack revolutionized human team coordination** - Khala revolutionizes AI agent coordination.

**No bosses. No bureaucracy. Just minds connecting through pathways, sharing insights, and coordinating through democratic communication.**

**The result:** Month-level AI autonomy through coordination infrastructure that scales with intelligence rather than fighting against it.

**En taro Adun. The minds unite through the Khala.** 🔮⚡

---

**Note:** The Khala is not just communication infrastructure - it's the foundation for democratic AI coordination that preserves individual agent autonomy while enabling collective intelligence.

**This is how AI systems coordinate to build better AI systems.**