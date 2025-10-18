# protoss

**Emergent AI coordination through conversation.**

Not a framework. A substrate. Two components: a transcript (bus) and agents that read it, think, and respond. Coordination emerges from dialogue. No orchestration. No state machines. No event schemas.

Agents hold constitutional identity. They don't execute tasks—they embody principles applied to context. The swarm coordinates itself.

---

## Start here

- **[doctrine.md](./docs/doctrine.md)** — Three core principles: conversation, constitution, cognition.
- **[architecture.md](./docs/architecture.md)** — The bus. The agent. The two databases.
- **[ascension.md](./docs/ascension.md)** — How it scales: channels, archons, self-repair.

Deeper: [cathedral.md](./docs/cathedral.md) (vision), [roadmap.md](./docs/roadmap.md) (path), [safety.md](./docs/safety.md) (guarantees).

---

## Quick Start

```python
import asyncio
from protoss import Protoss

async def main():
    swarm = Protoss(channel="work", base_dir="/tmp/protoss")
    await swarm.start()
    await swarm.send_human_message("Build a Flask API with user auth")
    await swarm.wait_for_completion(timeout=60)
    conversation = await swarm.get_conversation()
    print(conversation)

asyncio.run(main())
```

## Installation

```bash
pip install protoss
# or with poetry
poetry add protoss
```

Requires: Python 3.11+, `cogency` (for agent reasoning), OpenAI API key.

## How It Works

**The Bus:** Shared transcript. All coordination flows through it.

**The Agent:** Reads transcript. Applies constitutional identity. Responds. Loops.

**Three Constitutional Identities:**
- **Zealot** — Skeptical, uncompromising on code quality
- **Sentinel** — Anchors decisions in verified reality
- **Harbinger** — Surfaces core conflicts, demands clarity

Agents read each other. Consensus emerges. Task completes or times out.

---

## Contributing & License

This project is licensed under [Apache 2.0](./LICENSE). See [CONTRIBUTING](./CONTRIBUTING.md) for development setup.

---

*The reverent language throughout these docs is intentional. It's not marketing—it's constitutional transmission. The system doesn't enforce behavior through code. It transmits through narrative. Read deeply and you internalize the principles.*

**Complexity is sin. Simplicity is salvation.**
