# Mental Model Clarity: Protoss + Cogency Integration

*Preserving the fragile but crucial mental model for emergent coordination through conversation.*

## The Core Insight

Multi-agent coordination through conversation is **single-agent conversation scaled up**. Each agent thinks it's having a normal chat, but the "user" is actually the collective swarm conversation.

## The Two-Database Pattern

We have **two separate SQLite databases** with different purposes:

### 1. Public Conversation (`.protoss/store.db`)
- **What**: Shared channel messages visible to all agents
- **Examples**: "human: build todo app", "zealot: I'll handle backend"
- **Managed by**: Protoss Bus
- **Purpose**: The shared reality all agents coordinate around

### 2. Private Reasoning (`.cogency/store.db`) 
- **What**: Each agent's internal reasoning threads
- **Examples**: "§think: backend means database + API", "§call: create_file(...)"
- **Managed by**: Individual Cogency instances  
- **Purpose**: Private thoughts and tool executions per agent

## The Bridge Pattern

```
Public Conversation → Agent reads → Cogency reasoning → Agent responds → Public Conversation
```

**The Flow**:
1. **Agent reads** entire channel history from Protoss Bus storage
2. **Agent injects** this full history as "query" to its Cogency instance
3. **Cogency assembles** context from: public conversation (query) + private reasoning (its storage)
4. **Agent responds** back to Bus, which stores response in public conversation
5. **Cycle repeats** - all agents continuously re-read and respond

## Critical Mappings

| Cogency Concept | Protoss Mapping | Why This Works |
|-----------------|-----------------|----------------|
| `user_id` | Agent constitutional identity (`zealot`, `sentinel`, `harbinger`) | Enables profile learning and distinct reasoning patterns |
| `conversation_id` | Channel name (`human`, `task-alpha`) | Scopes context and enables parallel conversations |
| `query` | Full channel conversation history | The "user input" is the entire swarm discussion |

## Why This Architecture is Elegant

### 1. **Ephemeral Agents + Persistent Memory**
- **Agents**: Computationally ephemeral - can crash and restart
- **Memory**: Informationally persistent in SQLite
- **Bridge**: Context assembly connects them seamlessly

### 2. **Single Responsibility Layers**
- **Cogency**: Solves single-agent conversation + reasoning (proven, stable)
- **Protoss**: Solves multi-agent message routing (simple, focused)  
- **Bridge**: Agent reads Bus → injects to Cogency (clean interface)

### 3. **Constitutional Coordination**
- Each agent loads distinct constitutional identity from markdown
- Coordination emerges from constitutional reasoning over shared context
- No orchestration layer - pure conversation-driven emergence

## The Coordination Loop

```python
# Each agent runs this loop continuously
while agent.running:
    # Read shared public conversation from Bus
    history = bus.get_history(channel)
    
    # Format as single query for Cogency
    context = format_conversation(history)
    
    # Inject to private Cogency reasoning engine
    async for event in cogency_agent(
        query=context,
        user_id=agent_type,  # zealot/sentinel/harbinger 
        conversation_id=channel  # human/task-alpha
    ):
        if event["type"] == "respond":
            # Respond back to shared public conversation
            await bus.send(agent_type, event["content"], channel)
            
    # Brief pause before next coordination cycle
    await asyncio.sleep(2.0)
```

## Why Mental Model Fades

This architecture holds **four complex concepts simultaneously**:

1. **Cogency's ephemeral agents + SQLite persistence model**
2. **Protoss message routing + coordination patterns**  
3. **The bridge between public/private storage systems**
4. **Constitutional reasoning + emergence theory**

The complexity isn't architectural - it's **cognitive load**. Each piece is elegant, but holding them all in working memory is genuinely difficult.

## The Test

If you took **ONE agent** and fed it a conversation history containing messages from multiple agents, would it reason and respond appropriately?

**If yes** → the mapping is fundamentally sound  
**If no** → we're forcing square pegs into round holes

Based on Cogency's proven ability to handle complex conversation context, the answer should be **yes**.

## Implementation Status

Currently building the minimal prototype to validate this mental model:

- ✅ **Bus**: Simple message storage and routing
- ✅ **Agent**: Constitutional identity + Cogency integration  
- ✅ **Swarm**: 3 agents (zealot/sentinel/harbinger) coordination
- 🔄 **Bridge**: Fix Bus → Cogency context injection
- ⏳ **Test**: Validate emergent coordination through conversation

## The Litmus Test

Can 3 agents coordinate to build a todo app through pure conversation, with each agent maintaining private reasoning threads while participating in shared dialogue?

This test will prove or disprove the fundamental hypothesis.