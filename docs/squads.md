# Zealot Squads: Multi-Agent Coordination via Khala

**Deploy agents on shared pathway. Coordinate through Khala conversation.**

## Squad Pattern

```python
deploy_squad("Build auth system", ["zealot", "zealot", "stalker"])
```

**Natural coordination:**
- Zealot-1: "Taking backend API"
- Zealot-2: "Frontend integration" 
- Stalker: "Reviewing implementations"

## Implementation

### Continuous Reasoning
**Current:** `think → act → respond` (dies)
**Squad:** `think → act → respond → continue` (lives)

```python
:respond: Taking auth backend
:call: FileWrite(auth.py, code)
:respond: Auth complete, moving to tests
:call: SystemShell(pytest)
:respond: All tests pass
# Continues until objective done
```

### Squad Deployment

```python
async def deploy_squad(task: str, units: List[str]):
    squad_id = f"squad-{uuid.hex()}"
    
    # All units join same Khala pathway
    for unit_type in units:
        unit = create_unit(unit_type)
        unit.join_pathway(squad_id, task)
    
    # Coordinate through conversation
```

### Pathway Coordination

Each agent reads pathway messages before next cycle:
- What work others claimed
- What they completed  
- What needs doing

```python
# Agent continuous cycle
recent_msgs = pathway.get_messages(since=last_cycle)
context = f"Squad status: {recent_msgs}\nTask: {task}"
# Continue reasoning with squad awareness
```

### Quality Control

**Stalkers = Quality zealots with Guardian Protocol**

```
Zealot-1: "Auth system complete"
Stalker: "Guardian Protocol: JWT missing expiration check"
Zealot-1: "Fixed JWT validation"
Stalker: "APPROVED"
```

### Squad Types

```python
# Development
["zealot", "zealot", "stalker"]

# Research  
["zealot", "zealot", "archon"]

# Large tasks
["zealot", "zealot", "zealot", "stalker", "probe"]
```

## Escalation

When squads stuck:
```
Zealot-1: "Database migration failing"
Zealot-2: "Same issue here"
Stalker: "Need Sacred Four guidance"
```

Squad escalates to constitutional deliberation.

## Implementation Priority

1. **Extend Cogency** - `:respond:` as non-terminal
2. **Build `deploy_squad()`** - Multiple agents, shared pathway  
3. **Test coordination** - 3 agents, simple task
4. **Add Stalker QA** - Quality through conversation

## Result

**Natural task coordination through Khala conversation.**

No hierarchy. No ceremony. Just agents coordinating through shared pathway until objective complete.

En taro Adun. ⚔️