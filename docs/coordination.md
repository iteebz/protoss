# Multi-Agent Coordination: Essential Patterns

**How multiple agents work together through conversation until task completion.**

## Core Architecture Insights

### The Coordination Loop
```python
async def coordinate(self, task: str, channel_id: str) -> str:
    while cycle < max_cycles:
        # Get channel context and flatten for agent
        recent_messages = bus.get_history(channel_id)
        channel_context = flatten(recent_messages, config)
        
        # Run with fresh conversation_id
        agent = CogencyAgent(
            user_id=f"channel-{channel_id}",
            conversation_id=f"agent-{uuid4()}",  # Fresh memory each cycle
            instructions=self.identity
        )
        
        response = await agent.execute(user_message)
        await bus.transmit(channel_id, self.id, response)
        
        # Check completion signals
        if "[COMPLETE]" in response:
            return "Task completed"
        elif "[ESCALATE]" in response:
            await conclave.consult(response)
            return "Task escalated"
```

### Key Architectural Decisions

**Fresh Memory Per Cycle:**
- New conversation_id prevents context explosion
- Channel becomes shared persistence layer
- Agents get fresh perspective each cycle

**Attention Architecture:**
- Async read-execute cycles (agents choose sync timing) 
- Protects uninterrupted cognitive flow
- Empirically validated: continuous notifications degrade reasoning quality

**Protocol Tokens:**
- `[COMPLETE]` and `[ESCALATE]` for reliable parsing
- No LLM inference or word heuristics needed
- Agents choose when to use signals

**Channel Context as User Message:**
- Multi-agent coordination maps to single-agent conversation patterns
- Leverages existing cogency infrastructure without modification
- Clean abstraction boundary

## Coordination Patterns

### Single Agent Self-Coordination
Agent reads empty channel → reports progress → reads own history → continues → signals completion

### Multi-Agent Squad Coordination  
Multiple agents spawn into same channel → claim work through discussion → coordinate via channel messages → reach consensus

### Escalation Patterns
```python
"Unable to resolve database connection pooling. [ESCALATE]"
"Team split on microservices vs monolith approach. [ESCALATE]"
"Requirements unclear on user authentication method. [ESCALATE]"
```

## Anti-Patterns Eliminated

**Context Explosion:** Fresh conversation_id per cycle, channel as shared memory
**Attention Fragmentation:** Async coordination, agents choose sync timing  
**Hardcoded Workflows:** Pure conversation-based coordination
**Sycophantic Agreement:** Constitutional identities create productive disagreement
**Complex Completion Detection:** Simple protocol tokens

## Research Validation

**Claude Code Degradation (v1.0.52+):** 4x cognitive overhead from continuous notifications
**Sacred Four Deliberation:** Natural consensus through constitutional conversation
**Bridge First Contact:** 3 frontier models achieved consensus in 7 minutes without orchestration

**Lesson:** Respect agent attention architecture. Conversation-based coordination works at scale.

---

*Breakthrough: Treating agents as conversational participants rather than distributed computing nodes.*