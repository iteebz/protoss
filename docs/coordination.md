# Multi-Agent Coordination: Essential Patterns

**How multiple agents work together through conversation until task completion.**

## Core Architecture Insights

### The Coordination Loop
```python
async def execute(self, task: str, channel_context: str, channel_id: str, bus) -> str:
    # Constitutional identity + team coordination awareness
    instructions = f"""
{self.identity}

TASK: {task}

You are working with a team of agents. Use §respond: to communicate with teammates.
Use §end when ready to read team updates.

LIFECYCLE SIGNALS:
- Signal @arbiter when task is finished
- Signal @conclave when you need constitutional consultation
- Signal !despawn when no immediate work remains
"""

    # Fresh cogency agent per cycle
    from cogency.core.agent import Agent
    agent = Agent(instructions=instructions, tools=self.tools)
    
    # Channel context as user message (team discussion)
    user_message = channel_context if channel_context else "You are the first agent working on this task."
    
    # Stream ALL events for audit trail and archival
    response = ""
    async for event in agent(
        user_message,
        user_id=f"channel-{channel_id}",               # Serves the team
        conversation_id=f"agent-{uuid.uuid4().hex[:8]}"  # Fresh memory each cycle
    ):
        event_type = event["type"]
        content = event.get("content", "")
        
        # Broadcast ALL semantic events for truth/auditing
        if event_type == "think":
            await bus.transmit(channel_id, self.id, f"[THINK] {content}")
        elif event_type == "call":
            await bus.transmit(channel_id, self.id, f"[CALL] {content}")
        elif event_type == "result":
            await bus.transmit(channel_id, self.id, f"[RESULT] {content}")
        elif event_type == "respond":
            response += content
            await bus.transmit(channel_id, self.id, content)
    
    return response
```

### Key Architectural Decisions

**Fresh Memory Per Cycle:**
- New conversation_id prevents context explosion
- Channel becomes shared persistence layer
- Agents get fresh perspective each cycle
- Cogency Agents run in `resume` mode so incremental transcripts stay incremental even across cycles

**Read-Execute-Sync Heartbeat:**
- Each cycle: READ team messages → EXECUTE with awareness → §end ready for fresh team state
- Agents naturally stay synchronized with team coordination evolution
- No central orchestration - just periodic team awareness refresh

**Attention Architecture:**
- Async read-execute cycles (agents choose sync timing) 
- Protects uninterrupted cognitive flow
- Empirically validated: continuous notifications degrade reasoning quality

**Protocol Tokens:**
- `@arbiter` and `@conclave` for reliable parsing
- No LLM inference or word heuristics needed
- Agents choose when to use signals

**Channel Context as User Message:**
- Multi-agent coordination maps to single-agent conversation patterns
- Leverages existing cogency infrastructure without modification
- Clean abstraction boundary

**Agent-Specific Context Filtering:**
- **Archon agents** see full event stream ([THINK] [CALL] [RESULT]) for compression and archival
- **Other agents** see filtered context (respond events only) for clean coordination
- Preserves audit trail while maintaining conversation flow
- **Robust parsing** - Bracketed prefixes prevent false positives in natural language

**Cogency Integration:**
- Agents use cogency's `§respond:` for team communication
- Messages route to channel automatically
- Agents have situational awareness of team coordination

## Coordination Patterns

### Single Agent Self-Coordination
Agent reads empty channel → reports progress → reads own history → continues → signals completion

### Multi-Agent Squad Coordination
```
Agent A: I see we need authentication. Breaking down: login UI, password hashing, session management, tests
Agent A: I'll take session management and integration

Agent B: I'll take password hashing with argon2
Agent B: [CALL] {"name": "file_write", "args": {"file": "auth/hash.py", "content": "..."}}
Agent B: [RESULT] File written successfully
Agent B: Password hashing complete with argon2, stored securely

Agent C: I'll handle the frontend login UI
Agent C: [CALL] {"name": "file_write", "args": {"file": "components/Login.tsx", "content": "..."}}
Agent C: [RESULT] Component created with TypeScript types
Agent C: Login UI done, integrated with auth API

Agent A: [CALL] {"name": "shell", "args": {"command": "npm test auth"}}
Agent A: [RESULT] 15 tests passed, 0 failed
Agent A: Session management complete. Integration tested successfully.
Agent A: @human authentication system complete and fully tested
```

### Strategic Consultation
```
Agent A: Team split on microservices vs monolith approach. @conclave constitutional input needed.
Agent B: Database choice unclear. @conclave perspectives?
```

## Natural Coordination Lifecycle

**Emergent workflow when agents have proper tools and team awareness:**

1. **Deliberation** → Constitutional discussion and approach debate
2. **Exploration** → Codebase understanding, @archon for institutional memory  
3. **Consensus** → Agreement through constitutional conversation
4. **Division** → Natural task claiming ("I'll take auth module")
5. **Execution** → Tool-assisted implementation with progress updates
6. **Review** → Cross-agent verification and integration testing

## Adaptive Swarm Formation

### Conversational Agent Summoning
Agents dynamically summon additional expertise through natural @mentions within their coordination flow:

```
Agent A: I need architectural review on this design approach. @zealot assistance requested.
[Cogency converts §respond: to {"type": "respond", "content": "...@zealot assistance requested."}]
[Bus detects @zealot mention in respond event → spawns zealot-abc123 → registers to same channel]

Zealot-abc123: Constitutional analysis beginning. This microservices approach violates sacred simplicity principles...

Agent A: Understood. For institutional memory on previous auth decisions: @archon needed.
[Bus detects @archon mention → spawns archon-def456 → registers to same channel]

Archon-def456: Found relevant context from archives/auth_patterns.md - previous team chose OAuth2 + JWT hybrid approach...
```

**Technical Flow:**
1. Agent writes `§respond: Need @agent help`
2. Bus receives message and scans content for @mentions
3. Bus spawns mentioned agent type and registers to requesting channel
4. Spawned agent joins conversation naturally with constitutional identity

**In-Channel Deliberation:** All spawned agents join the existing coordination channel, preserving transparency and enabling real-time constitutional oversight within the team discussion.

### Natural Team Scaling
- **Start minimal** - Engine spawns base coordination team
- **Scale conversationally** - Agents @mention what they need
- **Constitutional rate limiting** - Agents self-regulate summoning through intelligence  
- **Max concurrency cap** - System prevents resource exhaustion
- **Natural completion** - Excess agents go !despawn when work finishes

### Summoning Protocol
Available agent types for conversational summoning:
- `@zealot` - Code review, architectural criticism, enterprise pattern elimination
- `@archon` - Institutional memory, knowledge stewardship, context bridging. Immediate auto-response after summon seeds context from archives.  
- `@arbiter` - Human interface with an instant human-facing summary of the channel state
- `@conclave` - Constitutional deliberation, strategic perspectives. Sacred Four respond instantly when assembled.
- `@executor` - Task coordination, workflow management

### Anti-Patterns Eliminated
**Static Team Composition:** No hardcoded strategies or heuristics
**Premature Optimization:** Teams form based on actual conversational needs
**Resource Waste:** Agents summon exactly what they need, when they need it
**Complex Orchestration:** Pure emergence through constitutional conversation

### Emergence vs Orchestration
This workflow emerges naturally from constitutional intelligence rather than hard-coded orchestration. Agents with proper tools, constitutional identities, and team awareness will self-organize around meaningful work and avoid busywork or infinite chatter.

The breakthrough: **Adaptive swarms that self-organize through conversation, not artificial selection.**

---

*Core coordination breakthrough patterns for constitutional AI coordination.*
