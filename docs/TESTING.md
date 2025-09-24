# Cathedral Grade Testing: The Arbiter of Architectural Truth

*This document codifies the sacred principles and characteristics of "Cathedral Grade Tests" within the Protoss project. These tests serve as the ultimate arbiter of architectural truth, ensuring that the implementation remains aligned with the constitutional vision and embodies the highest standards of purity and emergence.*

## The Mandate: Pragmatic Validation of Architectural Truth

Our testing philosophy is not driven by arbitrary coverage metrics, but by the profound necessity of validating the core architectural principles. Cathedral Grade Tests are designed to:

1.  **Affirm Constitutional Alignment:** Directly verify that the codebase manifests the principles enshrined in the Doctrines and the System Architecture.
2.  **Protect Interface Purity:** Ensure that the "Cathedral Interface" (`async with Protoss(...)`) and the public APIs of core components remain simple, elegant, and robust.
3.  **Validate Emergent Behavior:** Confirm that complex, intelligent coordination *emerges* from the interplay of sovereign agents, rather than being explicitly orchestrated.
4.  **Guard Against Architectural Drift:** Act as a constitutional resistance against complexity, ceremony, and any deviation from the project's core tenets.

## Characteristics of a Cathedral Grade Test

### 1. Constitutional Focus
-   **Direct Principle Validation:** Each test should, where possible, implicitly or explicitly validate a constitutional principle (e.g., "Cognitive Sovereignty is maintained," "Emergence is observed").
-   **Architectural Contract Verification:** Tests must confirm that components adhere to their defined architectural contracts (e.g., the Bus correctly routes messages, the Gateway spawns agents in isolation).

### 2. Interface-Driven Purity
-   **High-Level Entry Points:** Prioritize testing through the primary `Protoss` context manager for end-to-end validation.
-   **Public API Boundaries:** Unit tests should focus on the public interfaces of classes, treating internal implementation details as opaque.

### 3. Behavioral Clarity
-   **Observable Outcomes:** Assertions should focus on observable system behavior and the resulting state, rather than internal method calls or private attributes.
-   **Event-Driven Assertions:** For event-driven systems, assertions on the sequence, type, and content of emitted events are paramount.

### 4. AI-Centric Developer Experience (DX)
-   **Readability and Intent:** Tests must be clear, concise, and easily interpretable by an AI. Test names should be the shortest descriptive name that clearly articulates the architectural principle or behavior being validated. Since the test's file name provides the module scope, the function name should focus only on the specific case under test (e.g., `test_specific_case` is preferred over `test_module_for_a_specific_case`).
-   **Minimal Setup, Maximum Impact:** Fixtures should abstract away boilerplate, allowing the test body to focus on the specific scenario.

### 5. Strategic Mocking
-   **Centralized Fixtures:** Utilize `conftest.py` for reusable, well-defined mocks of external dependencies (e.g., `Khala`, `Bus`, `SQLite`).
-   **Behavioral Simulation:** Mocks should simulate the *behavior* of dependencies, especially for asynchronous interactions, to enable realistic scenario testing without actual external calls.
-   **`Cogency` Mocking:** Crucially, `Cogency` (the LLM engine) must be mocked to control LLM agent responses, allowing for deterministic testing of agent reasoning and coordination logic. This ensures that the *constitutional interpretation* of the agent is testable.

### 6. Resilience and Safety Validation
-   **Critical Signal Testing:** Thoroughly test the behavior of sacred guardrails like `!emergency` and `!despawn` to ensure their immediate and correct impact on the swarm.
-   **Persistence and Recovery:** Validate that critical state (e.g., message history, coordination status) is correctly persisted and recoverable.

## The Arbiter's Oath

Every Cathedral Grade Test is an oath to architectural purity. It is a declaration that the system, at its core, functions as intended by its constitutional design. These tests are not merely checks; they are affirmations of the Protoss vision.

⚔️ *En Taro Adun. Let the tests be pure, and the architecture eternal.*