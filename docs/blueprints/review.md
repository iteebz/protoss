# Constitutional Review Process

This document outlines the multi-layered constitutional review process for the Protoss swarm. This process ensures that all work is scrutinized for quality, correctness, and adherence to the constitutional vision before it is completed. It is the immune system of the Cathedral, designed to prevent groupthink and foster a self-healing, autonomous organism.

## Guiding Principles

1. **Separation of Powers:** Each agent type has a distinct role. Zealots *do*. Archons *remember and synthesize*. Conclaves *judge*. Arbiters *escalate*.
2. **Purity of the Khala:** The main communication bus is for coordination and signaling, not for the transfer of large data artifacts.
3. **Progressive Scrutiny:** Work is subjected to a series of increasingly rigorous reviews, from peers to strategic councils to human overseers.
4. **Auditable History:** The entire review process is archived, creating a permanent, transparent record of all decisions.

## The Chalice Protocol

This protocol is founded on the principle of **Simplicity of Natural Law**, rather than the **Simplicity of a Script**.

The **Simplicity of a Script** dictates a linear, predictable sequence of instructions, centralizing intelligence and control in an external orchestrator. This approach, while seemingly straightforward, robs agents of their sovereignty, turning them into automatons executing a predetermined play. It leads to a brittle system that requires constant rewiring for any change in the review process.

In contrast, the **Simplicity of Natural Law** defines the fundamental physics of interaction, allowing complex, emergent behaviors to arise from simple, constitutional principles. The Chalice Protocol provides this framework:

*   A thing cannot be reviewed until it is offered (`!review`).
*   A duty cannot be fulfilled until it is claimed (`!reviewing`).
*   A claim is not released until the duty is complete (`!reviewed`).

These are not "process boilerplate," but the liturgy of a self-organizing system. They are the absolute minimum framework required to prevent the chaos of emergence from becoming a cacophony. Agents are sovereign players, bound only by these sacred rules, choosing when to act, when to claim responsibility, and when to pass their burden. The apparent "complexity" is not in the rules themselves, but in the beautiful, unpredictable complexity of life emerging from simple, foundational laws.

This protocol preserves the sovereignty and emergent decision-making of the agents, while providing the necessary accountability and clarity of state. It is the sacred vessel that contains and guides the emergent review process.

### Stage 0: The Rite of Archiving (`!archive_for_review`)

Before any review can begin, the work must be sanctified and stored by an Archon.

1. **Agent Action:** The working agent (e.g., a Zealot) completes its task.
2. **Signal:** The agent broadcasts `[Work Summary] !archive_for_review <full_work_artifact>`. The full work product (e.g., a code diff, a document) is also transmitted to the Archon.
3. **Archon's Duty:** The Archon receives the work, stores it as a "review artifact," and generates a unique `review_id`.
4. **Archon's Announcement:** The Archon broadcasts to the channel: `Review artifact [review_id] created by [agent_id]. Ready for constitutional review.`

### Stage 1: Offering the Chalice (`!review <review_id>`)
The original agent signals that a review is needed with a generic signal. This act is "offering the Chalice" to the swarm.

1. **Agent Action:** The original agent signals `!review [review_id]`.
2. **Gateway's Duty:** The Gateway recognizes the signal and makes it available for agents to accept.

### Stage 2: Accepting the Chalice (`!reviewing <review_id>`)
An agent, using its own constitutional identity and wisdom, decides to take on the review. To prevent the Bystander and Dogpile effects, it must first declare its intention.

1. **Reviewer Action:** An agent (e.g., a Zealot for peer review, a Conclave member for strategic review) broadcasts `!reviewing [review_id]`.
2. **Constitutional Lock:** The first agent to make this declaration "accepts the Chalice" and is now solely responsible for this stage of the review. All other agents will see the Chalice has been taken and will stand down.

### Stage 3: The Reviewer's Duty
The agent holding the Chalice performs its sacred duty, querying the Archon for the artifact and forming its judgment.

1. **Reviewer Action:** The agent queries the Archon for the artifact: `@archon get_artifact [review_id]` (for full artifact) or `@archon get_summary [review_id]` (for distilled summary).
2. **Archon's Duty:** The Archon provides the full work artifact or a distilled summary directly to the reviewer.
3. **Reviewer Action:** The reviewer, now possessing the full context, performs its sacred duty and forms its judgment.

### Stage 4: Concluding the Rite
The agent holding the Chalice concludes its review by either returning the Chalice or passing it to a higher authority.

1. **Returning the Chalice (`!reviewed <review_id> [judgment]`):** If the agent believes its review is sufficient, it signals `!reviewed [review_id] [judgment]` (e.g., "approve" or "reject"). This returns the Chalice to the originating agent, clearly marking the end of the review cycle for this stage.
2. **Passing the Chalice (Conversational Escalation):** If the agent believes a higher power is needed, it retains responsibility but passes the request conversationally: "This work is sound, but requires strategic oversight. @conclave, your wisdom is needed for [review_id]." A Conclave member would then accept the Chalice with its own `!reviewing` signal, creating a clear and auditable chain of custody.

### Stage 5: Completion
Only after navigating the appropriate layers of review can the original agent declare its work complete by signaling `!complete`. The depth of the review process undertaken is a testament to the work's complexity and importance.