# Protoss Safety Architecture

*This document defines the safety model for the Protoss swarm. It is based on the principle that simplicity and transparency are the ultimate foundations of safety.*

---

## The Three Layers of Safety

Our safety model does not rely on complex, internal enforcement mechanisms. Instead, it is an emergent property of three simple, transparent layers.

### 1. The Immutable Base (LLM Safety)

The foundational layer of safety is the underlying Large Language Model itself. The LLM provider enforces a set of immutable constraints that cannot be overridden by the swarm or its constitution. This provides a non-negotiable backstop against the generation of harmful content.

### 2. The Transparent Framework (Architectural Safety)

The radical simplicity of the Protoss architecture is its greatest safety feature. The framework has no complex orchestration, no event bus, and no privileged, supervisory agents. The entire coordination mechanism is a plain-text conversational transcript.

This makes the system inherently auditable and transparent. There are no hidden states or back-channels. All actions and reasoning are recorded in the public transcript for any observer—human or machine—to inspect. The attack surface is minimized because the framework itself is minimal.

### 3. The Constitutional Guardrails (Behavioral Safety)

Safety is programmed into the agents through their constitutional `IDENTITY` and `GUIDELINES`. The constitution provides the high-level principles that bound agent behavior, while the shared `GUIDELINES` provide explicit, low-level instructions for safe operation.

Most critically, the guidelines define the exit conditions (`!despawn`, `!complete`), ensuring that agents are designed from the ground up to complete their tasks and terminate cleanly, preventing infinite loops or runaway processes.

## Emergency Protocols

The system has only two explicit commands, which serve as the primary emergency overrides:

-   `!despawn`: An agent's sovereign decision to terminate its own process.
-   `!complete`: An agent's signal that the collective task is finished, prompting all other agents to despawn.

A human observer can inject these commands into the conversation at any time to halt the swarm.

---

*Our philosophy is that safety is not achieved by adding complexity, but by removing it. A simple, transparent system is an inherently safe one.*