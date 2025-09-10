# Squads: Multi-Agent Deployment

**Deploy agents on shared pathway. Coordinate through conversation.**

## Squad Pattern

```python
deploy_squad("Build auth system", ["zealot", "zealot", "stalker"])
```

**Natural coordination:**
```
§PSI|squad-123|zealot-1: taking backend API
§PSI|squad-123|zealot-2: frontend integration
§PSI|squad-123|stalker-x: reviewing implementations
```

## Continuous Reasoning Breakthrough

**Traditional:** `think → act → respond` (dies)
**Squad:** `think → act → respond → continue` (lives)

**Agents persist on pathway until squad objective complete.**

## Squad Deployment

```python
async def deploy_squad(task: str, units: List[str]):
    squad_id = f"squad-{uuid.hex()}"
    
    # All units join same Khala pathway
    for unit_type in units:
        unit = create_unit(unit_type)
        unit.join_pathway(squad_id, task)
```

## Coordination Cycle

**Each agent before next execution:**
1. Read recent pathway messages
2. Understand what others claimed/completed
3. Choose next logical work  
4. Execute with squad context

## Squad Types

```python
["zealot", "zealot", "stalker"]          # Development
["zealot", "zealot", "archon"]           # Research  
["zealot", "zealot", "zealot", "stalker"] # Large tasks
```

## Design Phase Coordination

**Design debate → peer signoff → TDD/implementation split**

**Problem:** Eager agents dive into coding, add slop, require human course correction.

**Solution:** Force design phase coordination before implementation:
1. **Triage** - Initial exploration and problem understanding
2. **Design debate** - Twin agents discuss canonical approach against doctrine  
3. **Peer signoff** - Squad validates approach before coding
4. **Split execution** - One takes tests, other implementation

**Insight:** Cognitive phase separation prevents implementation momentum from steamrolling good design.

## The Pattern

**Natural task coordination through Khala conversation.**

No hierarchy. No ceremony. Agents coordinate through shared pathway until objective complete.

**En taro Adun.** ⚔️