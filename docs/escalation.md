# Escalation Protocol

**LLM metacognition + Constitutional deliberation + Binary human escalation.**

**No heuristics. No confidence thresholds. No ceremony.**

## Core Principle

**Uncertainty detection is an LLM metacognitive capability, not a mathematical threshold.**

Workers honestly assess: *"Am I making shit up with inference or do I actually need help?"*

Constitutional agents decide escalation necessity based on their governance context.

## Protocol Flow

### Stage 1: Worker Uncertainty Detection

**Zealot encounters decision boundary:**
```python
# Internal metacognitive check
metacognitive_prompt = """
I'm working on: {current_task}
I've reached this decision point: {specific_issue}

Am I making shit up with inference or do I actually need help with this decision?
If I need help: what specific guidance do I need?
"""
```

**If uncertain** → Escalate to Sacred Four:
```
§PSI:conclave-urgent:{zealot_id}:escalation:{specific_uncertainty_description}
```

### Stage 2: Constitutional Deliberation

**Conclave spawns Sacred Four** to deliberate on:

1. **Primary issue**: The original uncertainty that triggered escalation
2. **Escalation decision**: Does this require human intervention?

**Sacred Four contexts:**
- **Tassadar**: Pragmatic vision - "Can we ship a solution?"
- **Zeratul**: Deep investigation - "What are we missing?"  
- **Artanis**: Collaborative synthesis - "How do we unite perspectives?"
- **Fenix**: Direct execution - "What's the simplest path forward?"

**Binary outcomes:**
- **"We got this"** → Constitutional guidance back to worker
- **"Summon human"** → Escalate to Nexus with full context

### Stage 3: Human Escalation (When Needed)

**Constitutional deadlock or safety concerns** → Escalate to Nexus:
```
§PSI:nexus:conclave-{id}:escalation:Constitutional agents require human guidance on {issue}

Context:
- Original worker uncertainty: {worker_issue}
- Constitutional positions: {sacred_four_positions}
- Deadlock reason: {why_human_needed}
```

## Escalation Types

### Uncertainty Escalation
- **Trigger**: Worker metacognitive uncertainty
- **Target**: Constitutional 4
- **Resolution**: Guidance or human escalation

### Coordination Escalation  
- **Trigger**: Cross-agent coordination conflicts
- **Target**: Constitutional 4
- **Resolution**: Governance decision or human escalation

### Safety Escalation
- **Trigger**: Potential harm or security concerns
- **Target**: Direct to Constitutional 4 (or Nexus if critical)
- **Resolution**: Safety protocol or human override

## Implementation Details

### Worker Uncertainty Detection
```python
async def assess_uncertainty(self, current_context: str, decision_point: str) -> bool:
    """LLM metacognitive uncertainty assessment."""
    prompt = f"""
    Current task context: {current_context}
    Decision point: {decision_point}
    
    Honest self-assessment: Am I making shit up with inference or do I actually need help?
    
    Return: True if I need help, False if I can proceed confidently.
    """
    # Let LLM decide based on honest self-reflection
    return await self.agent.assess(prompt)
```

### Constitutional Response Patterns
```python
# Sacred Four deliberation patterns
constitutional_contexts = {
    "tassadar": "Pragmatic shipping decisions and strategic trade-offs",
    "zeratul": "Deep investigation and assumption questioning", 
    "artanis": "Collaborative synthesis and unity-building",
    "fenix": "Direct execution and complexity cutting"
}
```

## Anti-Patterns to Avoid

### ❌ Confidence Thresholds
```python
# WRONG: Mathematical certainty thresholds
if confidence < 0.7:
    escalate()
```

### ❌ Heuristic Rules
```python  
# WRONG: Predetermined escalation criteria
if task_complexity > threshold or risk_level == "high":
    escalate()
```

### ❌ Premature Human Escalation
```python
# WRONG: Bypassing Constitutional deliberation
if worker.uncertain:
    escalate_to_human()  # Skip Sacred Four
```

## Tuning Knobs

### Over-Escalation Management
- **Sacred Four memory**: Remember recent decisions to avoid repeated escalations
- **Context learning**: Archon logs successful uncertainty resolutions
- **Escalation feedback**: Track whether escalations were actually needed

### Under-Escalation Detection
- **Outcome monitoring**: Track task success rates for non-escalated uncertainties
- **Retrospective analysis**: Archon identifies missed escalation opportunities
- **Constitutional review**: Periodic Sacred Four assessment of escalation patterns

### Escalation Spam Prevention
- **Cooldown periods**: Prevent rapid re-escalation of same issues
- **Context deduplication**: Merge similar uncertainties into single deliberation
- **Priority routing**: Critical safety issues bypass normal flow

## Protocol Messages

### Worker → Constitutional 4
```
§PSI:conclave-urgent:{zealot_id}:escalation:{uncertainty_description}
```

### Constitutional 4 → Worker (Resolved)
```
§PSI:{zealot_id}:conclave-{id}:guidance:{constitutional_decision}
```

### Constitutional 4 → Human (Deadlock)
```
§PSI:nexus:conclave-{id}:escalation:{full_context_summary}
```

### Human → System (Resolution)
```
§PSI:conclave-{id}:nexus:resolution:{human_decision_and_reasoning}
```

## Success Metrics

### Efficiency Metrics
- **Escalation resolution time**: How quickly uncertainties get resolved
- **False escalation rate**: Percentage of escalations that weren't actually needed
- **Missed escalation rate**: Percentage of tasks that should have escalated but didn't

### Quality Metrics  
- **Task success rate**: Overall system capability with escalation protocol
- **Human intervention frequency**: How often humans actually need to step in
- **Constitutional consensus rate**: How often Sacred Four reach agreement

## Future Enhancements

### Advanced Metacognition
- **Uncertainty calibration**: Train workers to better assess their own uncertainty
- **Domain-specific escalation**: Different uncertainty patterns for different task types
- **Confidence evolution**: Track how worker uncertainty assessment improves over time

### Constitutional Learning
- **Escalation pattern recognition**: Sacred Four learn common uncertainty types
- **Governance precedent**: Build institutional memory of escalation decisions  
- **Adaptive deliberation**: Adjust Sacred Four contexts based on escalation patterns

---

**Bottom Line: Trust LLM metacognition. Let Constitutional agents decide. Keep humans in the loop without ceremony.**

**The escalation protocol preserves worker focus while ensuring governance oversight without hierarchical bullshit.**

En taro Adun.