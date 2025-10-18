# Protoss Safety Architecture

*Safety model: simplicity and transparency are the ultimate foundations.*

---

## Three Layers of Safety

No complex internal enforcement. Emergent property of three simple, transparent layers.

### 1. The Immutable Base (LLM Safety)

Foundational layer: the LLM itself. LLM provider enforces immutable constraints. Non-negotiable backstop against harmful content.

### 2. The Transparent Framework (Architectural Safety)

Radical simplicity is the greatest safety feature. No complex orchestration. No event bus. No supervisory agents. Entire mechanism: plain-text conversational transcript.

Inherently auditable and transparent. No hidden states. No back-channels. All actions and reasoning recorded in public transcript. Attack surface minimized because framework is minimal.

### 3. The Constitutional Guardrails (Behavioral Safety)

Safety programmed through constitutional `IDENTITY` and `GUIDELINES`. Constitution provides high-level principles. Guidelines provide explicit low-level instructions.

Exit conditions (`!despawn`, `!complete`) designed into framework. Agents complete tasks and terminate cleanly. No infinite loops. No runaway processes.

## Emergency Protocols

Two explicit commands serve as primary emergency overrides:

- `!despawn`: Agent's sovereign decision to terminate its process.
- `!complete`: Agent's signal that collective task is finished. All others despawn.

Human observer can inject these commands at any time to halt the swarm.

---

*Safety is not achieved by adding complexity. Safety is achieved by removing it. Simple, transparent systems are inherently safe.*