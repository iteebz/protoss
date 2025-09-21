# PROTOSS ROADMAP

**Implementation priorities, architectural decisions, and future work.**

## Scaling Philosophy

**Core Decision:** Scaling complexity kills coordination quality.

**Simple, Predictable Scaling:**
```python
await protoss("build REST API", agents=5)  # Human chooses agent count
```

**Design Principles:**
- **Cathedral principle**: Spend complexity budget on coordination patterns, not scaling mechanisms
- **Predictable resource usage**: No runaway scaling, clear capacity planning
- **Coordination focus**: Agents coordinate on work, not meta-work of scaling decisions
- **Human intelligence**: Humans judge task complexity → agent needs

**Anti-patterns Avoided:**
- ❌ Dynamic spawning (agents spawn more agents)
- ❌ Authority chaos (any agent can spawn agents)
- ❌ Natural language parsing for scaling requests
- ❌ Constitutional fluidity (dynamic identity adoption)

**Authority Model:** Human chooses count → Agents coordinate within bounds → System provides infrastructure

## Implementation Priorities

### Phase 1: Monitoring Foundation
- `protoss monitor` - Lightweight swarm minimap (active agents, channels, recent activity)
- `protoss status` - Current swarm state
- Basic visibility into coordination

### Phase 2: Conversational Interface  
- `protoss ask` - Strategic questions to Executor
- Escalation protocol - Units can summon human
- Constitutional guidance integration

### Phase 2.5: Resource Infrastructure
- lib/resources.py - Token usage, cost tracking, rate limiting
- Model call accounting across swarm coordination
- Budget awareness for task planning
- Performance metrics (tokens/task, coordination efficiency)

### Phase 3: Git Coordination
- Branch per unit strategy
- Bus-coordinated merges
- Conflict resolution protocol
- Rollback mechanisms for catastrophic failures

### Phase 4: Self-Improvement
- Meta-units that analyze coordination
- Safe self-modification protocols
- Recursive improvement validation

## Technical Implementation Challenges

### Git Coordination Strategy
**Problem:** Multiple units working simultaneously without repository conflicts

**Options:**
1. **Branch per unit:** Each unit gets git worktree, coordinated merges
2. **Atomic commits:** Units coordinate commit boundaries via Bus
3. **File-level locks:** Bus manages file access, prevents conflicts
4. **Conflict resolution protocol:** Conclave deliberation on merge conflicts

**Current thinking:** Branch per unit + Bus-coordinated merge strategy

### CLI Architecture Implementation
**Requirements:**
- Real-time monitoring stream
- Conversational interface 
- Command dispatch
- Escalation handling

**Options:**
1. **Rich Terminal UI:** textual/rich for real-time dashboard
2. **Infinite Loop CLI:** Like cogency simple pattern
3. **Multi-process:** Monitor in background, commands in foreground
4. **WebSocket UI:** Browser-based real-time interface

### Swarm Self-Improvement Protocol
**Core Question:** How does swarm work on itself without breaking itself?

**Approach:**
1. **Meta-units:** Special units that analyze coordination patterns
2. **Safe experimentation:** Test improvements in isolated environments  
3. **Gradual rollout:** Constitutional approval for self-modifications
4. **Rollback protocol:** Revert changes that degrade coordination

## Open Questions

- **Long channel optimization**: When/how to compress extended conversations
- **Multi-channel coordination**: If needed, how do channels communicate
- **Performance tuning**: Optimal context window size for different task types
- **Escalation routing**: Sophisticated routing beyond human/Conclave
- **Repository coordination**: Practical multi-agent git workflow
- **Self-modification safety**: Constitutional approval mechanisms for swarm evolution
- **Dynamic scaling**: If later needed, separate infrastructure layer with observable metrics

---

*Implementation priorities and future work for constitutional AI coordination.*