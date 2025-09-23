# Protoss Roadmap

*This document outlines the project's ultimate vision and the implementation priorities to achieve it.*

## The Grand Vision: Recursive Self-Improvement

The fundamental research question of the Protoss project is:

**Can a swarm of AI agents, coordinated by a constitutional framework, achieve breakthroughs in complexity that a single agent cannot? Can a swarm of Claude 5-level intelligences produce Claude 6-level research?**

The ultimate test of this is **Recursive Self-Improvement (RSI)**: the ability of the Protoss swarm to operate on and improve its own codebase, using the same coordination protocols it uses for any other task.

### RSI Success Metrics

Success is defined by the swarm's ability to work on the `protoss/` codebase to improve its own coordination architecture while simultaneously:

-   Working on external projects.
-   Maintaining constitutional code quality.
-   Escalating appropriately to human oversight for constitutional matters.
-   Evolving its own coordination capabilities.

If successful, the implication is that Protoss is a universal coordination substrate for any complex cognitive work, including the work of AI development itself.

---

## Implementation Phases

The following phases outline the path toward the grand vision of RSI.

### Phase 1: Foundational Infrastructure (Complete)
-   **Bus & Gateway**: The core messaging and agent-spawning mechanics.
-   **Data-Driven Agents**: The generic `Agent` class configured by the `AGENT_REGISTRY`.
-   **Core Doctrines**: The establishment of `constitution`, `emergence`, `resolution`, and `continuity`.

### Phase 2: Monitoring & Observability
-   `protoss monitor`: A lightweight, real-time view of the swarm (active agents, channels, recent activity).
-   `protoss status`: A snapshot of the current swarm state.
-   **Khala Visualization**: Real-time psionic network visualization for coordination flow analysis.
-   This phase provides the basic visibility required for effective human oversight.

### Phase 3: Conversational Interface & Resource Management
-   `protoss ask`: A mechanism for posing strategic questions to the `@arbiter`.
-   **Escalation Protocol**: Formalizing the process by which agents can summon a human.
-   **Resource Tracking**: Implementing token usage, cost tracking, and rate limiting to make the swarm budget-aware.

### Phase 4: Advanced Coordination Patterns
-   **Git Coordination**: A robust protocol for multi-agent work on a single codebase (e.g., branch-per-task, bus-coordinated merges, conflict resolution via `@conclave`).
-   **Multi-Channel Coordination**: Defining how agents can coordinate across different channel contexts if needed.
-   **Constitutional Evolution**: AI systems authoring their own constitutional frameworks based on coordination experience.
-   **Multi-Swarm Federation**: Protocols for coordination between sovereign cathedral instances with different constitutional identities.

### Phase 5: Recursive Self-Improvement
-   **Meta-Coordination Agents**: Units that can analyze the swarm's own coordination patterns.
-   **Safe Experimentation**: Isolated environments for testing self-modifications.
-   **Constitutional Approval Flow**: The process by which the swarm proposes changes to its own constitution for human review, as defined in `SAFETY.md`.
