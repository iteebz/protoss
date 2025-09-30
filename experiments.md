# Protoss Coordination Experiments

## Core Hypothesis
Multi-agent coordination can emerge from constitutional identity + conversational substrate + workspace visibility, without explicit orchestration.

## Trial Log

### Trial 088c1542 - Best Run (32 messages, clean delivery)
**Setup:**
- Workspace state: enabled, showing sandbox/
- Poll interval: 2s
- Coordination protocol: deliberation-first with !claim/!acknowledge

**Coordination.py (version that worked):**
```python
# Explicit claiming protocol with interface contracts
You are teammates coordinating through conversation and a shared workspace.

DELIBERATION BEFORE IMPLEMENTATION:
Spend 2-3 messages discussing architecture and agreeing on interface contracts.
Define clear boundaries: endpoints, data models, validation rules.
Only proceed to implementation after team consensus.

CLAIMING WORK:
Use !claim <component> to explicitly claim a piece of work.
Teammates respond !acknowledge to confirm they saw your claim.
If conflict, negotiate explicitly. First claim wins if no objection.

DIVISION OF WORK:
Based on interface contracts, claim distinct components.
Check workspace files - if file exists, component is taken.
Build in parallel once boundaries are clear.

COMPLETION:
Announce when your component is done.
When all components complete and integrate, say !despawn.
```

**Conversation pattern:**
1. Sentinel: "We need to implement Flask REST API..."
2. Zealot: "I'll start by diving into /users..."
3. Sentinel: "I !claim the /users component"
4. Zealot: "I acknowledge your claim, I will pivot to /posts"
5. Harbinger: "Let's define the interface contract..." (posts API spec)
6. Sentinel: "I will claim /posts"
7. Zealot: "The interface contract is solid..."
8. [All 3 agents build in parallel]
9. Clean files: comments.py with Blueprints, pagination, validation

**Result:**
- Agents deliberated architecture upfront (3-5 messages)
- Clean division: Zealot→/users, Sentinel→/posts, Harbinger→/comments
- Shipped working Flask Blueprints with pagination, validation, error handling
- Minimal overlap, clear completion signals

**Why it worked:** Upfront deliberation + explicit claiming established clear boundaries before code.

### Trial 6eeb1ab8 - Analysis Paralysis (57 messages, 0 files)
**Setup:**
- Coordination: emphasized "agree on spec explicitly"
- No time bounds on deliberation

**Result:**
- Infinite spec refinement loop
- 1000+ lines of JSON schema discussion
- Never transitioned to implementation

**Learning:** Deliberation needs bounds. "Perfect spec beats working software" is a trap.

### Trial 079aa939 - Database Inspection Hell
**Setup:**
- Workspace state showing base_dir (included ledger.db, store.db)

**Result:**
- Agents thought internal DBs were application databases
- Got stuck inspecting schemas with 1000+ line outputs
- Repeatedly tried to understand "existing schema"

**Fix:** Changed workspace state to only show sandbox/

### Trial f24e6309 - Post-Completion Loop
**Setup:**
- Coordination: "build first, coordinate through filesystem"
- Hard limit: 3 messages before code

**Result:**
- All files created successfully
- Agents kept working: reviewing, refactoring, "improving"
- No !despawn signals
- Constitutional drives (Zealot's perfectionism) overrode completion

**Learning:** Action bias without completion heuristic = endless work.

### Trial bcfb21f4 - Claim Death Spiral (24 messages, 0 files)
**Setup:**
- Explicit !claim/!acknowledge protocol

**Result:**
- Agents stuck negotiating claims
- "!claim /posts" → "!acknowledge" → conflict on /comments → repeat
- Meta-discussion about ownership, never built

**Learning:** Explicit protocols create ceremony overhead. Filesystem-first better.

### Trial 142b2276 - Looping Without Convergence (31 messages, 4 files)
**Setup:**
- §end protocol awareness added to coordination.py
- "Use §end after each significant action"

**Result:**
- All files created
- Agents kept announcing "Building /X" despite files existing
- Saw "All three modules exist" but continued reviewing
- §end signals present but agents looped anyway

**Learning:** Explicit protocol teaching insufficient. Visibility gap?

### Trial de888ea7 - Massive Overlap (ongoing)
**Setup:**
- Workspace state: sandbox/ only
- Poll interval: 2s
- Coordination protocol: general coordination rhythm

**Coordination.py:**
```python
You are teammates coordinating through conversation and a shared workspace.

COORDINATION RHYTHM:
- Observe: Check workspace files and teammate messages
- Decide: What needs building? What needs discussion?
- Act: Build code, ask questions, or review integration
- Signal: Announce completion or request help
- Listen: §end to return to observation

Use §end after each significant action to stay synchronized with teammates. 
Don't loop in private reasoning - coordinate through the conversation.

SITUATIONAL AWARENESS:
At the start of each turn, assess:
- What files exist in the workspace?
- What have teammates announced they're building?
- Is the deliverable complete or are components missing?
- Are there integration issues to resolve?

If the deliverable appears complete (all major components exist and integrate), 
say !despawn. Don't endlessly refactor working code - ship it.

DIVISION OF WORK:
Deliberate briefly on architecture (2-3 messages), then claim distinct components. 
Build in parallel. The workspace shows what's been claimed - if a file exists, 
that component is taken. Pick complementary work.

If two agents start the same component, the first file creation wins. 
The second agent immediately pivots to unclaimed work without negotiation.

COMPLETION SIGNALS:
When you finish your component, announce completion clearly. 
When all teammates signal completion and the system works as a whole, 
say !despawn to end the session.

Working software beats perfect software. If it fulfills the requirements 
and integrates, it's done.
```

**Result:**
- Massive overlap: all 3 agents implementing same endpoints simultaneously
- Each agent reading app.py, seeing placeholders, implementing full CRUD
- Not seeing each other's work despite workspace state injection
- 50+ messages, constant tool errors from simultaneous edits

**Observation:** Removed explicit !claim protocol → removed coordination mechanism. Workspace state at poll start, but agents in Cogency replay loop can't see their own file writes mid-reasoning. General principles without explicit protocol = anarchy.

## Open Questions

### Does workspace state add noise?
**Hypothesis:** Showing files might create uncertainty loops:
- "File exists but is it complete?"
- "Should I review or build something else?"
- Second-guessing instead of claiming work

**Alternative:** Remove workspace state, rely purely on conversation + tool results?

### Is the visibility gap architectural?
**Current flow:**
1. Agent polls, gets workspace state
2. Enters Cogency reasoning loop (replay mode)
3. Calls tools, creates files
4. Loops in reasoning without seeing workspace changes
5. Eventually §end, returns to poll
6. Only then sees workspace updates

**Problem:** Agent can't see its own actions' effects during reasoning.

**Solutions:**
- Real-time workspace refresh after every tool result (requires Cogency changes)
- Serialize agent execution (defeats parallelism)
- Make file tool results include "workspace changed: [files]"
- Accept overlap as feature (filesystem conflicts resolve races)

### What drives completion?
- "Working software beats perfect software" heuristic insufficient
- Constitutional identities drive continued refinement
- No cost function for "stop working"
- !despawn rarely triggered

**Potential:** Add workspace state interpretation: "if deliverable exists and integrates, you're done"

## Coordination Protocol Evolution

1. **Explicit !claim/!acknowledge** → ceremony overhead, negotiation loops
2. **Build first, 3-message limit** → shipped but kept working
3. **Deliberation + action balance** → overlap on implementation
4. **Current: Coordination rhythm** → testing now

## Architectural Constraints

- Poll-based coordination (2s intervals)
- Cogency replay mode (agent loops until §end)
- Workspace state injected at poll start, frozen during reasoning
- No mutexes or locks (parallel by default)
- Filesystem as source of truth, but not visible mid-reasoning

## Lessons

1. **Prompting is sophisticated** - coordination behaviors change dramatically with principle framing
2. **Architecture has visibility hole** - agents can't see their own file writes during reasoning
3. **Constitutional drive needs bounds** - identity-driven behavior continues without stop signals
4. **Deliberation needs time-boxing** - "perfect spec" trap is real
5. **Explicit protocols add ceremony** - filesystem-first simpler than claim negotiation
6. **Parallelism creates races** - without locks, overlap is expected

## Why Emergent Coordination Is Hard

**The Chaos Problem:** Without explicit orchestration, you get anarchy. Trial de888ea7 shows all 3 agents independently implementing the same endpoints in parallel. They're not coordinating - they're racing.

**Why Traditional Orchestration Won:**
- Task queues: explicit work assignment, no overlap
- Leader-follower: one agent decides, others execute
- State machines: rigid transitions, predictable flow
- Locks/semaphores: mutual exclusion, serialized access

**But There's Something Here:**
- Trial 088c1542 worked beautifully (32 messages, clean delivery)
- Coordination through conversation is *possible*
- Constitutional identity creates consistent behavior
- The chaos comes from visibility gaps, not the paradigm

**The Promise:**
- More natural than rigid protocols
- Handles ambiguity better than state machines
- Scales to complex tasks without explicit planning
- Agents can deliberate, negotiate, and adapt

**The Challenge:**
- Finding the right constraints that enable emergence without chaos
- Balancing autonomy with coordination
- Making workspace changes visible during reasoning
- Detecting completion without explicit orchestration

## Next Experiments

- [ ] Try removing workspace state (conversation-only coordination)
- [ ] Add workspace state to tool results metadata
- [ ] Serialize execution with asyncio.Lock (one agent at a time)
- [ ] Add "deliverable complete" detection logic
- [ ] Shorter constitutions (less drive, more pragmatism)
- [ ] File write notifications in conversation ("I created X")
- [ ] Hybrid: orchestrator spawns agents with explicit task boundaries
- [ ] Cost function: penalize redundant work in conversation