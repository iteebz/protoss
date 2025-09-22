# PROTOSS ROADMAP

**Implementation priorities, architectural decisions, and future work.**

## Scaling Philosophy

**Core Decision:** Emergent scaling through constitutional dialogue, not explicit orchestration.

**Emergent Scaling Principles:**
- **Human provides Vision:** The human initiates coordination with a high-level vision (`async with Protoss("build X")`).
- **Agents self-organize:** Agents, guided by their constitutional identities, dynamically summon additional expertise via `@mentions` as needed.
- **Bus/Gateway handles spawning:** The Bus, leveraging Gateway's pure spawning functions, creates new agent processes in response to `@mentions`. (For foundational definitions of Bus and Gateway, refer to [Emergence: The Constitutional Language of the Swarm](coordination.md)).
- **Constitutional safeguards:** `max_agents` per channel prevents resource exhaustion. (See [Emergence: The Constitutional Language of the Swarm](coordination.md) for more on constitutional principles).
- **Focus on coordination:** Complexity budget is spent on robust coordination patterns, not on explicit scaling mechanisms.

**Anti-patterns Avoided:**
- ❌ Centralized orchestration of agent lifecycles.
- ❌ Rigid, predefined workflows for scaling.
- ❌ Micromanagement of agent counts by the human beyond the initial vision.

**Authority Model:** Human provides vision → Agents emerge and coordinate → System provides infrastructure and safeguards.

## Implementation Priorities

### Phase 1: Monitoring Foundation
- `protoss monitor` - Lightweight swarm minimap (active agents, channels, recent activity)
- `protoss status` - Current swarm state
- Basic visibility into coordination

### Phase 2: Conversational Interface  
- `protoss ask` - Strategic questions to Arbiter
- Escalation protocol - Units can summon human
- Constitutional guidance integration

### Phase 2.5: Resource Infrastructure
- `lib/resources.py` - Token usage, cost tracking, rate limiting
- Model call accounting across swarm coordination
- Budget awareness for task planning
- Performance metrics (tokens/task, coordination efficiency)

### Phase 3: Git Coordination
- Branch per unit strategy
- Bus-coordinated merges
- Conflict resolution protocol
- Rollback mechanisms for catastrophic failures

### Phase 4: Self-Improvement (Safety aspects to be covered in SAFETY.md)
- Meta-units that analyze coordination patterns.
- Safe experimentation in isolated environments.
- Constitutional approval for self-modifications (human oversight).
- Rollback protocols for changes that degrade coordination.

## Technical Implementation Challenges

### Git Coordination Strategy
**Problem:** Multiple units working simultaneously without repository conflicts

**Current thinking:** Branch per unit + Bus-coordinated merge strategy, with constitutional deliberation for complex conflicts.

### CLI Architecture Implementation
**Requirements:**
- Real-time monitoring stream (`protoss monitor`)
- Conversational interface (`protoss ask`)
- Command dispatch
- Escalation handling

**Approach:** Leverage existing `protoss monitor` and `protoss ask` for real-time visibility and human interaction. Further enhancements will be driven by coordination friction.

## Open Questions

- **Long channel optimization**: When/how to compress extended conversations.
- **Multi-channel coordination**: If needed, how do channels communicate.
- **Performance tuning**: Optimal context window size for different task types.
- **Escalation routing**: Sophisticated routing beyond human/Arbiter.
- **Repository coordination**: Practical multi-agent git workflow.
- **Dynamic scaling**: How to constitutionally scale the swarm beyond initial human input, while maintaining emergent principles.
- **Self-modification safety**: Covered in SAFETY.md.

---

*Implementation priorities and future work for constitutional AI coordination.*