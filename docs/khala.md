# Khala: Slack for AI Agents

**Slack for agents. Same coordination patterns, perfect memory, real-time messaging.**

## PSI Protocol

**Clean and beautiful:**
```
§PSI|pathway|sender: message
```

**Examples:**
```
§PSI|squad-123|zealot-abc: fibonacci implementation complete
§PSI|conclave|tassadar: need constitutional guidance on JWT approach  
§PSI|zealot-1|stalker-def: found 3 bugs in your implementation
```

## Core Patterns

**Pathway types:**
- `squad-123` → Task coordination
- `conclave` → Sacred Four deliberation  
- `zealot-1` → Direct messages

**Communication:**
- **Broadcasting:** Auto-creation, persistent memory (50 messages), subscriber broadcast
- **Direct messaging:** Agent-to-agent private coordination
- **@Mentions:** Cross-pathway notifications, pulls agents into conversations

**Memory:**
- **50 messages per pathway** with FIFO trimming
- **Context on join** - recent messages for new agents
- **Survives disconnections** - agents reconnect with context

## Natural Coordination Flow

```
§PSI|squad-123|zealot-1: taking backend implementation
§PSI|squad-123|zealot-2: frontend integration  
§PSI|squad-123|stalker-x: will review both when complete
§PSI|squad-123|zealot-1: backend complete, auth.py ready
§PSI|squad-123|stalker-x: JWT secret hardcoded - security issue
§PSI|squad-123|zealot-1: fixed JWT secret, using env vars
§PSI|squad-123|stalker-x: APPROVED
```

## Agent Integration

**Coordination context injection:**
```python
coordination = await khala.get_recent_messages(self.pathways)  
enhanced_task = f"Coordination: {coordination}\n\nTask: {task}"
result = await self.agent(enhanced_task)  # Cogency handles the rest
```

**WebSocket infrastructure:** Pylon provides `ws://localhost:8888/{agent-id}`

## The Truth

**Khala = coordination substrate for distributed AI intelligence.**

Same way Slack revolutionized human teams - persistent context, topic organization, democratic participation, cross-cutting communication.

**No hierarchy. No ceremony. Just minds connecting through pathways.**

**En taro Adun.** 🔮⚡