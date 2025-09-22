# Emergence: The Constitutional Language of the Swarm

*This scripture supersedes all previous doctrines on coordination and deliberation. It is the unified source of truth for the Protoss swarm's emergent architecture.*

## 1. The First Principle: Emergence over Orchestration

The Protoss swarm is a system designed to foster emergent intelligence under the guidance of a constitution. Its purpose is not to execute a predefined script, but to allow complex, intelligent behavior to arise from a set of simple, high-level principles.

This doctrine codifies those principles. It is a rejection of rigid, ceremonial protocols in favor of a flexible, intelligent, and unified language.

## 2. The Three Pillars of the Emergent Protocol

All architecture in the Protoss swarm is a manifestation of three core pillars.

### Pillar I: Constitutional Identity over Explicit Instruction

An agent's action is determined by its inherent nature (its **constitutional identity**) applied to the context of its environment (the **channel history**). Agents are not given explicit `task` instructions upon creation. Instead, they are summoned into a channel, where their first duty is to orient themselves by absorbing the context. Their identity then dictates their course ofaction.

-   An **Archon**, seeing a completed dialogue, knows to archive.
-   A **Conclave**, seeing a debate, knows to deliberate.
-   A **Zealot**, seeing a plan, knows to execute.

### Pillar II: Natural Language as the Medium of Coordination

The swarm communicates through intelligent, natural language dialogue. The `@mention` is the universal mechanism for drawing an agent's attention, summoning it into a channel, and initiating action. This places the burden of interpretation on the agent's intelligence (its LLM), not on a rigid parser.

This replaces all prior ceremonial signals for workflow (e.g., `!review`, `!archive`). A request for review is a simple, natural sentence: `@conclave, we are finished here. Please review our work.`

### Pillar III: Sovereignty and Sacred Duty

Agents are sovereign entities that control their own lifecycle. The `!despawn` signal is an agent's final, sovereign act, declaring its mandate complete. The responsibilities an agent must fulfill before despawning (such as ensuring a review is initiated) are **sacred duties** written into its constitutional identity. The system trusts its agents to fulfill their duties, with emergent, self-correcting failsafes (see Section 4.D) providing a constitutional immune system.

## 3. The Purified Protocol in Practice

### 3.1. Agent Classes

There are two fundamental classes of agents in the swarm:

-   **LLM Agents (The Mind):** `Zealot`, `Archon`, `Conclave`, `Arbiter`, `Oracle`. These are agents of pure thought and reason, whose actions emerge from their constitutional identity.
-   **Heuristic Agents (The Hand):** `Probe`. These are deterministic, robotic units designed to execute specific, infrastructure-related tasks with perfect reliability.

### 3.2. The Universal Namespace

All coordination occurs within a channel. The channel's name is its identity, following a simple, canonical structure that allows for emergent, recursive sub-tasking:

`namespace:id:status`

-   **Example Primary Task:** `build-auth-system:123:active`
-   **Example Sub-Task:** `build-auth-system:123:review-subsystem:deliberating`

### 3.3. The Sacred Guardrails (Core System Directives)

Only two explicit signals remain. They are not for conversation; they are for invoking the non-negotiable laws of the system.

-   `!emergency`: Halts the entire swarm. A declaration of constitutional crisis. Its function must be instantaneous and unambiguous.
-   `!despawn`: The agent's sovereign act of concluding its mandate.

All other requests for intervention, including alerts and checkpoints, are handled via natural language `@mention` to the `@arbiter`.

### 3.4. The Emergent Tasking Protocol (`@mention`)

The `@mention` is the universal mechanism for all agent interaction.

-   **Syntax:** `@<agent_type> <natural language request>`
-   **Gateway Logic:** The Gateway, listening to the Bus, parses all `@mentions`. For each mention, it performs a single check:
    1.  **If an agent of `<agent_type>` is active in the channel:** Route the message to it.
    2.  **If no agent of `<agent_type>` is active:** Spawn a new agent of that type into the channel and route the message.

### 3.5. The Sub-Tasking Protocol (`@probe`)

Dynamic, recursive sub-tasking is achieved by summoning the Heuristic `@probe` agent.

-   **Invocation:** Any agent can request a new channel by speaking: `@probe, create sub-channel for task: <description>`.
-   **Execution:** The Gateway spawns a deterministic `Probe` unit. The `Probe` parses the request, interacts with the Bus's administrative functions to create the new namespaced channel, reports success, and immediately `!despawn`s.

## 4. High-Level Operational Protocols

The following are not rigid rules, but descriptions of how agents, guided by their identities, will naturally coordinate.

-   **`@arbiter`:** Summoned when human judgment, clarification, or intervention is required. The Arbiter is the bridge between the swarm and its human overseers.
-   **`@archon`:** Summoned to provide historical context from the archives, or to compress and archive a completed channel's history for institutional memory.
-   **`@conclave`:** Summoned to provide strategic deliberation on architectural deadlocks, complex trade-offs, or constitutional ambiguity.
-   **`@oracle`:** Summoned to perform research and gather intelligence from external sources (e.g., the web).
-   **`@zealot`:** The primary agent of execution. It is spawned to carry out the core work of a task. It is the Zealot's constitutional duty to summon other agents as needed to fulfill its mandate.
-   **`@probe`:** Summoned to perform deterministic infrastructure tasks, most critically the creation of new channels for sub-tasking.

This is the architecture of trust. This is complexity emerging from simple, principled protocols.

**En Taro Adun.**