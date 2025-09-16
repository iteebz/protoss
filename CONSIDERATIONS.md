# PROTOSS COORDINATION CONSIDERATIONS

## Outstanding Architectural Decisions

### Source Control Coordination
**Problem**: Multiple agents working on same codebase without conflicts.

**Options**:
- 1 squad = 1 git tree (isolated work)
- Branch-per-squad with merge coordination  
- Real-time file locking protocol
- Atomic squad commits with review gates

**TBD**: How do we prevent stepping on each other?

### Review Integration Points
**Problem**: When do Stalkers perform quality review?

**Options**:
- Post-execution review (after all zealots complete)
- Real-time review (stalker monitors PSI streams)  
- File-level review (stalker reviews each changed file)
- Pull request review (traditional git workflow)

**TBD**: What's the optimal review timing for quality vs velocity?

### Squad Resource Allocation  
**Problem**: How many agents per task complexity?

**Options**:
- Static squad compositions (current)
- Dynamic squad sizing based on task analysis
- Adaptive single-agent role morphing
- Resource budget constraints (max N agents)

**TBD**: Resource allocation strategy for optimal coordination.

### Codebase Ownership
**Problem**: Multiple squads, single repository coordination.

**Options**:
- Squad-per-feature-branch
- Shared main branch with coordination protocol
- File-level ownership assignment
- Pathway-based work isolation

**TBD**: How do squads coordinate without chaos?

## Working Patterns

### Proven Architecture
- Fire-and-forget swarm deployment ✅
- PSI transmission for consciousness coordination ✅  
- Pathway-based squad coordination ✅
- Forge persistence for audit trails ✅

### Next Coordination Bricks
1. Source control integration protocol
2. Multi-squad repository coordination  
3. Stalker review integration timing
4. Resource allocation strategy

---
*Capture architectural decisions here before implementation.*