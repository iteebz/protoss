# PROTOSS INTERFACE DESIGN

**Keep the surface austere: expose the Khala, skip the chrome.**

## Current Coordination Surface

- `protoss coordinate` boots the engine, spawns the first agents, and prints a plain-text status block.
- `protoss status` and `protoss config` report configuration snapshots; there are no dashboards or progress meters on top.
- The canonical interface is the Bus transcript. Agents speak in-channel, humans watch the same feed, and `@arbiter` mentions escalate when someone actually needs you.
- Monitoring right now means tailing logs or querying stored channel history. There is intentionally no visualization layer between the human and the constitutional conversation.

## Interaction Principles

- **Shared transcript.** Humans consume exactly what agents emit; no alt-reality UI exists for the operator.
- **Conversational escalation.** Mentions (`@arbiter`) replace bespoke prompts or modal workflows.
- **Thin surface, thick core.** Improvements must land in the engine or agents. Wrapper scripts stay boring on purpose.

## Future Work: Interface Enhancements

Track ideas here and keep them off the critical path until coordination friction justifies the investment:
- Live `protoss monitor` stream that mirrors Bus traffic without rooting through raw logs.
- Text-mode dashboards (textual/rich) when single-screen visibility demonstrably helps debug autonomy stalls.
- Browser visualizations if external observers need richer telemetry than the raw transcript.
- Conversational helpers like `protoss ask` or `protoss meta` once the engine exposes strategic or meta-coordination endpoints.

Park the gloss. Build the constitutional substrate first.
