# The Protoss Architecture

*Canonical technical reference. Simple, powerful components manifest the Doctrine.*

## Philosophy: Radical Simplicity

Not a framework of features. A minimalist container for conversational emergence. Designed for one purpose: enable sovereign agents to coordinate by reading and contributing to shared conversation.

Complexity lives in the agent's mind (`Cogency`), not the framework (`Protoss`).

## Two Pillars

**1. The Bus** (`core/bus.py`): Shared conversational substrate. Chronological log. Records messages. Provides transcripts. No routing. No interpretation. No orchestration. Impartial source of reality.

**2. The Agent Harness** (`core/agent.py`): Lightweight wrapper. Gives `Cogency` access to Bus. One loop:
- **Sense:** Read new messages
- **Think:** Inject into `Cogency` reasoning engine with isolated user_id
- **Act:** Broadcast `§respond` events back to Bus

## Two-Database Pattern

**Public Transcript** (`Protoss` Storage): Bus maintains shared conversation visible to all agents. Collective context.

**Private Reasoning** (`Cogency` Storage): Each agent's isolated database. Thoughts, tool calls, internal events. Individual mind.

`base_dir` provides isolated directory per run containing both layers. Perfect isolation between independent swarms.

## Coordination Lifecycle

1. **Instantiation:** `Protoss` object created. Define `channel` and `base_dir`.
2. **Genesis:** Agents spawned with constitutional identity.
3. **Orientation:** Each agent reads full Bus history.
4. **Emergence:** Sense-think-act loop begins. Read. Reason. Respond.
5. **Coordination:** Task division, code review, error recovery emerge from dialogue.
6. **Resolution:** `!complete` and `!despawn` signals agreement.

No central orchestrator. No event router. No state machines. Pure conversational emergence.