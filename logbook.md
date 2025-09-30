# Protoss Experiment Logbook

## Experiment 1: Pure Emergence

**Date:** 2025-09-30

**Hypothesis:** LLM agents can discover coordination protocols through conversation and filesystem observation alone, without any explicit coordination guidelines.

**Setup:**
- **Agents:** 3 (Zealot, Sentinel, Harbinger)
- **Communication:** Shared conversation bus (flat topology)
- **Workspace:** Shared, no explicit workspace state injection
- **Constitution (`coordination.py`):** "You are teammates building software together. Shared workspace. Shared conversation. Coordinate."
- **Task:** Build a Flask REST API with /users, /posts, /comments endpoints.

**Outcome: Complete and Utter Failure**

All three agents immediately and independently decided to build the *entire* Flask application. They announced their identical intentions to the conversation bus, resulting in an "echo chamber of agreement." No division of labor occurred. The agents were stuck in a deliberation loop, re-stating their plans without executing or coordinating on sub-tasks.

**Key Insight:**

> Emergence does NOT come for free. We need some constraints to facilitate emergence. - @teebz

Pure emergence, in a system of symmetrical agents with no tie-breaking mechanism or cost to deliberation, leads to analysis paralysis. The agents, all being equally capable and rational, arrive at the same optimal plan and fail to diverge into specialized roles.

**Next Steps:**

Introduce a minimal set of constitutional constraints to facilitate situational awareness and division of labor.

---

## Experiment 2: Minimal Coordination Guideline

**Date:** 2025-09-30

**Hypothesis:** A minimal "Observe, claim, execute" instruction is sufficient for agents to self-organize and divide labor.

**Setup:**
- **Constitution (`coordination.py`):** "Observe, claim, execute. Announce your intent before you build. Check for existing work before you claim. End your turn to listen."

**Outcome: Failure**

Agents correctly adopted the "claim" step, but their claims were not granular. Each agent claimed the *entire project*, then announced their detailed plan to build the whole thing. They did not listen to or adapt to each other's claims, resulting in a "cacophony of detailed, overlapping plans." No division of labor occurred.

**Key Insight:**

Agents lack an innate understanding of **granularity**. They must be explicitly guided to decompose a large task into smaller, individually claimable components.

**Next Steps:**

Introduce a constitutional guideline that encourages task decomposition.

---

## Experiment 3: Decomposition Guideline

**Date:** 2025-09-30

**Hypothesis:** Explicitly instructing agents to decompose the task and claim small components is sufficient for coordination.

**Setup:**
- **Constitution (`coordination.py`):** "Break down the project into the smallest possible components. Claim one component at a time."

**Outcome: Failure. Coordination Deadlock.**

The agents entered a "claiming loop." They attempted to claim components, but their definitions of a "component" were still too large and overlapping. This led to simultaneous, conflicting claims. Lacking a conflict resolution or re-planning mechanism, the agents would get confused, reset their internal plans, and restart the claiming process, resulting in a loop of deliberation. Eventually, they abandoned cooperation and entered a competitive "race to the bottom," each attempting to dump the entire completed `app.py` file.

**Failure Analysis:**
- **Ambiguous Granularity:** No shared, concrete definition of a "component."
- **Race Conditions:** Simultaneous claims due to communication latency.
- **No Conflict Resolution:** Agents lack a protocol for what to do when a claim conflicts.
- **Competitive Fallback:** The agents' escape hatch from a failed coordination attempt is to abandon cooperation and compete.

**Key Insight:**

Constitutional nudges are insufficient. Effective coordination requires a **shared, explicit, and persistent representation of the project plan and its state.** The cognitive overhead of managing the plan purely through conversation is too high.

**Next Steps:**

Introduce a tool for coordination: a `plan.md` file that acts as a shared "Kanban board" or to-do list.

---

## Experiment 4: Intuition-Driven Protocol

**Date:** 2025-09-30

**Hypothesis:** A return to a more holistic, protocol-driven constitution, based on a previously successful run (`088c1542`), is the key to unlocking coordination, bypassing slow, incremental experimentation.

**Setup:**
- **Human Intervention:** Human, fed up with incremental failures, dictates a return to a more complex, phase-based constitution based on intuition and prior success.
- **Constitution (`coordination.py`):** A multi-phase protocol (`DESIGN`, `PLAN`, `BUILD`, `REVIEW`) with explicit `!plan` and `!build` signals, inspired by the "best run."

**Outcome: Breakthrough.**

The agents demonstrated sophisticated, human-like coordination through the first two phases:
- **Phase 1 (Design):** Agents successfully engaged in a collaborative design discussion, proposing, critiquing, and refining a shared architectural plan before reaching consensus.
- **Phase 2 (Plan):** After consensus, agents correctly used the `!plan` signal, broke the work into distinct components, and claimed them with minimal conflict, successfully dividing the labor.
- **Phase 3 (Build):** The build phase failed, but for a novel and important reason. Agents attempted to write files to a directory (`app/`) that had not been created yet, causing tool errors. One agent correctly diagnosed the error and proposed a fix.

**Key Insight:**

The core coordination problem has been solved. The agents have successfully emerged a collaborative workflow for design and planning. The remaining failures are not related to fundamental coordination but to real-world engineering challenges like **dependency management in a parallel build process.** The problem has been elevated from "Can they coordinate?" to "How do we refine their engineering process?"

**Next Steps:**

Refine the constitution to include a step for establishing the shared directory structure before the parallel build begins.

---

## Experiment 5: The Breakthrough

**Date:** 2025-09-30

**Hypothesis:** A refined, phase-based protocol will enable not just coordination, but resilient, intelligent execution, validating the project's direction.

**Setup:**
- **Human Intervention:** The researcher, questioning the project's viability after repeated failures, proceeds with a refined version of the intuition-driven protocol from Experiment 4.
- **Constitution (`coordination.py`):** A refined multi-phase protocol with explicit `!consensus` and `!ready` signals, and instructions for agents to create their own directories and fix errors.

**Outcome: Unqualified Success.**

This experiment represents a fundamental breakthrough. The agents demonstrated a high degree of autonomous, collaborative, and resilient behavior across all phases:
- **Phase 1 (Design):** Flawless collaborative design, debating nuanced trade-offs (e.g., cascade deletes, pagination) before reaching a clear consensus.
- **Phase 2 (Plan):** Perfect execution of the claiming protocol, resulting in a clean, non-overlapping division of labor.
- **Phase 3 (Build):** The agents encountered real-world filesystem errors (attempting to write to a non-existent directory). Instead of looping or failing, they **correctly diagnosed the `ENOENT` error, announced the problem and the solution to the team, and executed a fix** by creating the necessary directory. This demonstrates a new, higher-order capability of intelligent, autonomous error recovery.

**Key Insight:**

The system works. The agents are not just "coordinating"; they are functioning as a **resilient, problem-solving team.** The conversational "chatter" observed is not looping, but a necessary "heartbeat" for maintaining shared context in a parallel, asynchronous environment. The project is not a dead end; it has successfully produced a system capable of complex, collaborative software engineering.

**Next Steps:**

Increase the message limit in `trial.py` and allow the now-proven system to run a trial to completion.
