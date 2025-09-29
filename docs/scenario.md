# Current Mental Model - Ephemeral Agent Coordination

**Date:** 2025-09-29  
**Status:** Work in Progress - Gaps Identified

## Core Architecture

**Agents are ephemeral processes:**
- Spawned by @mention in #human channel
- Run until !despawn or system signal
- Manage their own lifecycle

**Single channel coordination:**
- Everything happens in #human 
- No separate agent channels
- Pure conversation as coordination primitive

## Current Flow

```
Human: "build sentiment analysis @zealot" → #human
Bus: detects @zealot, spawns zealot process  
zealot-a1b2: "CLAIM: building sentiment analysis engine" → #human
zealot-a1b2: works...
zealot-a1b2: "COMPLETE: engine deployed" → #human  
zealot-a1b2: !despawn (process dies)
```

## IDENTIFIED GAPS

### 1. **Coordination Explosion - THE BIG ONE**
```
Human: "build sentiment analysis @zealot"
zealot-a1b2: spawns, starts working...

Human: "also fix the login bug @archon"
archon-c3d4: spawns, needs context about existing work

Human: "update the docs too @oracle"
oracle-e5f6: spawns, needs context about sentiment engine AND login bug

Human: "actually change the sentiment engine to use transformers"
??? WHO SEES THIS? zealot-a1b2 already working on old spec
```

**Problem:** Existing agents need context injection about new requests/changes.
**Gap:** How do running agents get updated context from #human?

### 2. **Context Loading for Existing Agents**
- Agent spawns and reads #human history to get context
- But history grows rapidly with multiple concurrent tasks
- How does agent filter relevant context vs noise?
- What if human changes requirements mid-stream?

### 3. **Claim Scope Ambiguity** 
- Is "build sentiment analysis" one claim or many?
- If zealot @mentions archon for help, is that a sub-claim?
- How do we prevent duplicate work when multiple agents spawn?

### 4. **Completion Authority in Multi-Agent**
- If 3 agents are working on related tasks, who decides "mission complete"?
- What if human is satisfied but agents think more work needed?
- What if agents complete but human wants changes?

### 5. **Agent Death and Handoff**
- zealot-a1b2 crashes mid-work
- How do other agents know to pick up the work?
- Is the claim orphaned or does someone inherit it?

## CURRENT IMPLEMENTATION GAPS

### Bus Kernel Needs:
- [ ] CLAIM parsing from agent messages
- [ ] Context injection mechanism for running agents  
- [ ] Claim inheritance/handoff protocol
- [ ] Multi-agent completion coordination

### Constitutional Questions:
- Should agents coordinate among themselves or through human?
- How does constitutional emergence work with concurrent tasks?
- What are the minimal coordination primitives needed?

## NEXT STEPS

1. **Test simple case first:** Single agent, single task, no concurrency
2. **Build context injection:** How do agents get updates mid-stream?
3. **Design handoff protocol:** What happens when agents die?
4. **Test coordination explosion:** Multiple concurrent tasks

---

**Key Insight:** The ephemeral agent model is clean for simple cases but coordination explosion reveals the complexity we're trying to solve.