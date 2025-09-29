# The Protoss Architecture

*This document is the canonical technical reference for the Protoss system. It describes the simple, powerful components that manifest the principles of the Protoss Doctrine.*

## 1. The Core Philosophy: Radical Simplicity

The architecture is a direct reflection of the Doctrine. It is not a framework of features, but a minimalist container designed to enable conversational emergence. Its entire design is optimized for a single purpose: to allow multiple, sovereign agents to coordinate their actions by reading and contributing to a shared conversation.

Complexity resides in the agent's mind (`Cogency`), not in the framework's code (`Protoss`).

## 2. The Two Pillars of the Framework

The Protoss framework consists of only two components:

1.  **The Bus (`core/bus.py`):** The shared conversational substrate. It is a simple, chronological log of all messages sent within a channel. It has only two functions: to record messages and to provide historical transcripts to agents. It does not route, interpret, or orchestrate. It is the impartial source of shared reality.

2.  **The Agent Harness (`core/agent.py`):** A lightweight wrapper that gives a `Cogency` instance access to the Bus. Its sole responsibility is to perform the coordination loop:
    *   **Sense:** Read new messages from the Bus.
    *   **Think:** Inject the messages as context into its internal `Cogency` reasoning engine.
    *   **Act:** Broadcast the `§respond` events from `Cogency` back to the Bus.

## 3. The Two-Database Pattern

To honor the doctrine of a two-level mind, the architecture uses two distinct storage layers:

1.  **The Public Transcript (`Protoss` Storage):** The Bus maintains the shared conversation, visible to all agents. This is the collective context.

2.  **Private Reasoning (`Cogency` Storage):** Each agent's internal `Cogency` instance maintains its own private database of thoughts (`§think`), tool calls, and other internal events. This is the agent's individual mind.

The `base_dir` parameter, set at the `Protoss` level, provides a single, isolated directory for each run, containing both the public transcript and the private reasoning databases for all agents in that run. This ensures perfect isolation between independent swarms.

## 4. The Coordination Lifecycle

A coordination event unfolds with profound simplicity:

1.  **Instantiation:** A `Protoss` object is created, defining the `channel` and `base_dir` for the run.

2.  **Genesis:** Agents are spawned into the channel. Each agent's harness is given a constitutional identity (`zealot`, `sentinel`, etc.).

3.  **Orientation:** Upon spawning, each agent reads the full history of the Bus to understand the current context.

4.  **Emergence:** The agents begin their sense-think-act loop. They read new messages from the Bus, reason about them using their private memory and constitutional identity, and contribute their responses back to the shared conversation.

5.  **Coordination:** Agents coordinate by reading each other's responses. Task division, code review, and error recovery emerge naturally from this shared dialogue, guided by the principles in each agent's constitution.

6.  **Resolution:** The task is complete when the agents conversationally agree it is done, signaled by the `!complete` and `!despawn` commands as defined in their constitutional `GUIDELINES`.

This architecture has no central orchestrator, no event router, and no complex state machines. It is the purest expression of conversational emergence.