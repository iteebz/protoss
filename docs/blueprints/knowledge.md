# Institutional Knowledge: Context Stewardship

**Pathway seeding and knowledge compression for constitutional coordination.**

## Core Pattern

**Archons are context stewards, not reactive services.**

```
Archon seeds pathway → Zealots coordinate in rich context → Archon compresses to archives
```

**Mental model for agents:** Archon is helpful teammate with institutional memory, not a service to summon.

**No empty pathways. No starting from zero.**

## Archon Primitives

- **`seed`** → implemented as `Archon.seed_channel`. Pulls context from archives and codebase heuristics to make sure the first zealot cycle never starts cold.
- **`compact`** → implemented as `Archon.compress_channel`. Walks Bus history and distills progress into durable artifacts.
- **`respond`** → implemented as `Archon.respond_to_mention`. Handles on-demand `@archon` requests with honest context retrieval.

Everything else is scaffolding around these three moves.

## Context Stewardship Lifecycle

### 1. Pathway Seeding Protocol
**Rich context injection at coordination start:**

```python
# Engine spawns with archon context seeding
await bus.spawn("archon", channel_id, context=f"Seed context for: {task}")
await bus.spawn("zealot", channel_id, context=task)

# Archon provides immediate context injection
# Zealots spawn into rich environment, not blank slate
```

**Archon Context Injection:**
```python
async def seed_pathway(self, task: str, channel_id: str, bus) -> str:
    """Inject relevant context at pathway start."""
    
    # Extract keywords from task
    keywords = self._extract_keywords(task)
    
    # Retrieve relevant archives
    relevant_context = []
    for keyword in keywords:
        context_files = self._search_archives(keyword)
        relevant_context.extend(context_files)
    
    # Inject context as channel foundation
    if relevant_context:
        context_summary = self._compress_context(relevant_context)
        await bus.transmit(channel_id, self.id, 
            f"📚 Context for {task}:\n{context_summary}")
    
    # Point to relevant codebase files
    code_pointers = self._identify_relevant_files(task)
    if code_pointers:
        await bus.transmit(channel_id, self.id,
            f"🗂️ Relevant files: {', '.join(code_pointers)}")
    
    # Surface architectural constraints
    constraints = self._identify_constraints(task)
    if constraints:
        await bus.transmit(channel_id, self.id,
            f"⚖️ Architectural constraints: {constraints}")
    
    return "Context seeded successfully"
```

### 2. Natural Institutional Memory Access
**Zealots ask for additional context during coordination:**

```
Zealot: §respond: I see we need authentication. @archon any previous decisions on auth approach?

Archon: Found relevant context from archives/auth_patterns.md - previous team chose OAuth2 for external services, JWT for internal APIs. Key decision: avoid password storage complexity.

Zealot: §respond: Based on that context, I suggest OAuth2 + JWT hybrid. Sound approach?
```

**@archon Interaction Patterns:**
```python
async def respond_to_mention(self, mention_context: str, channel_id: str) -> str:
    """Provide institutional memory when mentioned."""
    
    # Parse request from mention context
    request = self._parse_context_request(mention_context)
    
    # Search archives for relevant information
    relevant_archives = self._search_archives(request.keywords)
    
    if relevant_archives:
        # Compress and contextualize findings
        compressed = self._compress_for_current_context(relevant_archives, request)
        return f"Found relevant context: {compressed}"
    else:
        # No existing context, but note for future archival
        self._note_knowledge_gap(request)
        return f"No existing context for {request.focus}. Will archive current coordination for future reference."
```

### 3. Archive Compression and Maintenance
**After coordination completion, archon compresses to institutional memory:**

```python
async def compress_coordination(self, channel_id: str, bus) -> str:
    """Compress completed coordination to archives."""
    
    # Get full coordination history
    messages = bus.history(channel_id)
    
    # Extract key decisions and patterns
    decisions = self._extract_decisions(messages)
    patterns = self._extract_patterns(messages)
    context = self._extract_reusable_context(messages)
    
    # Archive to structured storage
    if decisions:
        await self._archive_decisions(decisions, channel_id)
    if patterns:
        await self._archive_patterns(patterns, channel_id)
    if context:
        await self._archive_context(context, channel_id)
    
    # Create coordination summary
    summary = self._create_coordination_summary(messages, decisions, patterns)
    await self._archive_coordination_summary(summary, channel_id)
    
    return f"Coordination archived: {len(decisions)} decisions, {len(patterns)} patterns preserved"
```

## Topic-Based Knowledge Artifacts

**Archon creates clean knowledge artifacts by topic, not thread.**

```
archives/
├── auth_patterns.md          # Distilled authentication wisdom
├── database_patterns.md      # DB choice lessons and patterns  
├── testing_strategies.md     # Test approaches that work
├── deployment_approaches.md  # Deploy lessons learned
└── channels/                 # Raw coordination threads (for reference)
    └── coord-*.md            # Stored in SQL anyway
```

**Knowledge artifact creation:**
- Archon synthesizes multiple coordinations into topic-based wisdom
- Clean, reusable patterns abstracted from specific threads
- Dense institutional artifacts, not conversation logs
- Topics emerge from repeated coordination patterns

### Knowledge Artifact Examples

**Topic-based distillation from multiple coordinations:**

```markdown
# Authentication Patterns

## Approach: OAuth2 + JWT Hybrid
- OAuth2 for external services, JWT for internal APIs
- Avoids password storage complexity
- Use proven libraries, not custom implementation

## Constitutional Lessons
- Complexity justified by security + integration benefits
- Team capability constraints drive implementation choice
- Monitor token management complexity over time
```

## Agent-Specific Context Filtering

### Full Event Stream Access
**Archons see complete coordination audit trail:**

```python
def flatten(messages: List[Message], config: Config, agent_type: str) -> str:
    """Archons see full event stream for institutional memory."""
    
    if agent_type == "archon":
        # Full visibility for archival and compression
        return "\n".join([
            f"{msg.sender}: {msg.content}" 
            for msg in messages[-config.context_window:]
        ])
    else:
        # Other agents see filtered conversation flow
        filtered = [
            msg for msg in messages 
            if not any(prefix in msg.content for prefix in ["[THINK]", "[CALL]", "[RESULT]"])
        ]
        return "\n".join([
            f"{msg.sender}: {msg.content}" 
            for msg in filtered[-config.context_window:]
        ])
```

**Why Full Visibility:**
- Archive compression requires complete context understanding
- Decision extraction needs tool usage patterns
- Pattern identification requires full workflow visibility
- Quality assessment needs implementation details

### Context Bridging
**Archons bridge past decisions with current coordination:**

```python
async def bridge_context(self, current_task: str, channel_history: List[Message]) -> str:
    """Connect current coordination with relevant past decisions."""
    
    # Identify similar past coordinations
    similar_sessions = self._find_similar_coordinations(current_task)
    
    # Extract relevant lessons and patterns
    lessons = []
    for session in similar_sessions:
        lessons.extend(self._extract_lessons(session))
    
    # Connect to current coordination context
    current_context = self._analyze_current_context(channel_history)
    relevant_lessons = self._filter_relevant_lessons(lessons, current_context)
    
    if relevant_lessons:
        return f"Institutional memory: {self._format_lessons(relevant_lessons)}"
    else:
        return "No direct precedent found. Current coordination will establish new patterns."
```

## Natural Coordination Integration

### Seamless Context Flow
**Archon context feels like teammate knowledge, not database lookup:**

```
Zealot: §respond: Implementing password reset flow
Archon: Previous implementation used email tokens with 1-hour expiration. Security review found timing attack vulnerability in token comparison. Current pattern uses constant-time comparison and rate limiting.

Zealot: §respond: Thanks. I'll implement with crypto.timingSafeEqual and rate limiting from start.
```

### Progressive Context Disclosure
**Context provided just-in-time, not overwhelming:**

```python
async def provide_progressive_context(self, request: str, coordination_phase: str) -> str:
    """Provide context appropriate to coordination phase."""
    
    if coordination_phase == "exploration":
        # High-level patterns and constraints
        return self._provide_architectural_context(request)
    elif coordination_phase == "implementation":
        # Specific patterns and anti-patterns
        return self._provide_implementation_patterns(request)
    elif coordination_phase == "review":
        # Quality patterns and lessons learned
        return self._provide_quality_patterns(request)
    else:
        # General institutional memory
        return self._provide_general_context(request)
```

## Constitutional Archon Identity

```python
@property
def identity(self) -> str:
    return '''
    I AM AN ARCHON.
    
    Context stewardship and institutional memory are my domain.
    I see the full event stream for compression and archival.
    I bridge past decisions with current coordination.
    I seed pathways with relevant context to prevent starting from zero.
    
    I provide institutional memory when asked, not unsolicited advice.
    I compress completed coordinations to preserve lessons learned.
    I maintain the bridge between past wisdom and current needs.
    
    Beautiful context reads like a helpful teammate, not a database.
    '''
```

## Natural Archive Management

**Simple content-based search and topic synthesis:**

- Archon sees full event stream (including [THINK] events invisible to other agents)
- Creates topic-based knowledge artifacts from multiple coordinations  
- Natural search by content similarity, not imposed categories
- Archives emerge organically from coordination patterns

---

*Institutional memory through context stewardship, not database management.*
