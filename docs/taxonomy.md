# Protoss Taxonomy

**Meme integrity maintained. Technical precision achieved.**

## Core Components

**NEXUS** - High-level interface  
- Receives human goals
- Orchestrates coordination
- Routes to appropriate systems

**PYLON** - Communication bus  
- WebSocket message routing
- `§PSI:target:source:type:content` protocol
- Powers all coordination

**GATEWAY** - Zealot spawner  
- Creates Cogency agents on demand
- Manages agent lifecycle  
- Spawns → Execute → Despawn

**ZEALOT** - Worker agent  
- Single task execution
- Cogency-powered
- Streams results via Pylon

## Communication Flow

```
Human → Nexus → Gateway → Zealot
         ↓        ↓       ↓
       Pylon ←────────────┘
```

## Protocol

**Atomic message**: `§PSI:target:source:type:content`  
**Types**: escalation, report, request, command, archive

## Upgrade Paths (Future)

- **Templar** = Council oversight + human escalation
- **Archon** = Memory system (Khala)
- **Warp Gate** = Advanced deployment

**MVP SCOPE: Nexus + Pylon + Gateway + Zealot**

My life for Aiur.