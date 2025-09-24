# Protoss System Architecture

*This document is the canonical technical reference for the Protoss system. It describes the concrete components and interaction patterns that manifest the principles laid out in the Doctrines.*

## 1. Core Architectural Philosophy

The system is designed as a decentralized, emergent swarm of sovereign agents coordinating through a central message bus. The architecture prioritizes functional purity, statelessness, and a clean separation of concerns, rejecting monolithic classes and inheritance in favor of data-driven behavior.

## 2. The Three Core Components

The architecture consists of three primary components:

1.  **The Bus (`bus.py`)**: The central nervous system of the swarm. It is a WebSocket server that handles all message routing between agents. Critically, it is also responsible for initiating the agent spawning process by listening for `@mention` signals in messages and triggering the appropriate Gateway function.

2.  **The Gateway (`gateway.py`)**: A library of pure, stateless functions. Its sole purpose is to handle the creation of new agent OS processes. It is invoked by the Bus and does not hold any state about the swarm.

3.  **The Agent (`agent.py`)**: A single, generic agent implementation. There are no subclasses for different agent types. An agent's specific identity, behavior, and capabilities are determined at runtime by the data it loads from the `AGENT_REGISTRY`.

### 2.4. The Cogency Core: The Agent's Stone

The Protoss Agent, while generic in its implementation, is not an empty vessel. Its core cognitive capabilities, its ability to reason, to parse protocol, to execute tools, and to manage its internal state, are powered by the `Cogency` library.

`Cogency` serves as the fundamental "stone" of the Protoss Agent. It provides:
-   **The ReAct Loop**: The core reasoning and action cycle.
-   **The Streaming Protocol**: The `§`-delimited communication for efficient LLM interaction.
-   **Stateless Context Assembly**: The robust mechanism for rebuilding agent memory from durable storage.

Thus, `Cogency` is not an external dependency; it is woven into the very fabric of the Protoss Agent's atomic unit. It is the engine of its thought, the interpreter of its will, and the foundation of its cognitive sovereignty.

## 3. Agent Identity: The Data-Driven Model

The system's most crucial pattern is its rejection of class inheritance for agent identity. An agent's "soul" is not defined by its code structure but by the data it is given upon creation.

-   **`AGENT_REGISTRY`**: This dictionary, located in `src/protoss/agents/registry.py`, is the single source of truth for agent definitions. It maps an agent type (e.g., `"conclave"`) to its constitutional components:
    -   `identity`: A list of identity texts that define the agent's core purpose and personality.
    -   `guidelines`: The behavioral guidelines and patterns the agent should follow.
    -   `tools`: The set of capabilities available to the agent.

-   **Instantiation**: When the Gateway spawns a new agent process, it passes an `agent_type` as an argument. The generic `Agent` class uses this type to look up its data in the `AGENT_REGISTRY` and assembles its unique persona and capabilities.

## 4. The Coordination Lifecycle

A typical coordination event unfolds as follows:

1.  **Vision Seeding**: A user initiates a task via the high-level `Protoss` interface, which acts as a temporary, specialized client for the duration of the mission.

    ```python
    async with Protoss("My vision @arbiter") as swarm:
        result = await swarm
    ```

2.  **Session Genesis**: The `Protoss` context manager (`__aenter__`) summons a temporary `Bus` instance for the session and connects to it.

3.  **Invocation**: The `Protoss` client sends the initial vision as a message to the `nexus` channel on the Bus.

4.  **Emergent Spawning**: The `Bus` processes the message and detects the `@arbiter` mention. It calls the stateless `gateway.should_spawn()` function. If the conditions are met, it invokes `gateway.spawn_agent("arbiter", ...)`.

5.  **Agent Creation**: The Gateway function creates a new operating system process running the generic `agent.py` module, passing `"arbiter"` as the `agent_type`.

6.  **Self-Discovery**: The newly created Arbiter agent starts, looks up its identity and guidelines in the `AGENT_REGISTRY`, and connects to the Bus.

7.  **Constitutional Dialogue**: The Arbiter reads the channel history, understands the vision, and begins its work, potentially invoking other agents via `@mentions`, which continues the cycle of emergence.

8.  **Resolution**: The `Protoss` client passively awaits a completion signal. Its `__await__` method monitors the `nexus` channel specifically for a message from an `arbiter` agent containing a completion keyword (e.g., "complete", "done").

9.  **Session Dissolution**: Upon receiving the signal, the `await` completes, the `async with` block exits, and the `Protoss` instance disconnects and shuts down its session Bus.

## 5. Channel Taxonomy

The Khala uses structured channel names following the pattern `{purpose}:{identifier}:{status}` to enable self-documenting coordination. Core channels include `nexus` for vision seeding, `task:*` for work coordination, `query:*` for human questions, and `conclave:*` for Sacred Four deliberation.
