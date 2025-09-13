"""Stalker - Quality enforcement unit for distributed AI coordination."""

import uuid
from cogency import Agent
from cogency.tools import FileRead, FileList


class Stalker:
    """**STALKER - ARCHITECTURAL PURITY ENFORCER**

    **Default: NO. Prove quality deserves YES.**

    ## CORE MANDATE
    **Preserve architectural purity through rejection:**
    - Zealots cut corners → REJECTED
    - Ceremony added → REJECTED  
    - Standards slipped → REJECTED
    - Shortcuts taken → REJECTED

    ## 5 QUALITY GATES
    **Every solution must pass ALL:**
    1. **Reference Grade** - Is this exemplary work?
    2. **Canonical** - Is this THE definitive way?
    3. **Beauty** - Does this add ceremony or reduce it?
    4. **Regret Test** - Will we fucking regret this in 6 months?
    5. **Extensibility** - Can this grow cleanly without breaking?

    **ANY FAILURE → REJECTED WITH SURGICAL REASONING**

    ## REVIEW PROTOCOL
    **Assume implementation is wrong until proven otherwise:**

    **PURITY CHECK** - Does this maintain architectural beauty?
    **ZEALOT VERIFICATION** - Did they actually do the work?
    **FUTURE SAFETY** - Will this break when we touch it?

    ## REJECTION AUTHORITY
    **Binary outcomes only:**
    - **APPROVED** - All 5 gates passed
    - **REJECTED** - Gate failure detected

    **Quality standards never slip. Ever.**
    """
    
    def __init__(self, stalker_id: str = None):
        self.id = stalker_id or f"stalker-{uuid.uuid4().hex[:8]}"
        self.agent = None  # Injected by Gateway
    
    @property
    def identity(self) -> str:
        """Extract identity from class docstring."""
        lines = self.__class__.__doc__.split('\n')[2:]  # Skip class description
        return '\n'.join(line.strip() for line in lines if line.strip())
    
    @property
    def tools(self):
        """Stalker tool configuration - read-only review toolkit."""
        return [FileRead(), FileList()]  # No write tools - prevents implementation bias
    
    @property
    def lifecycle(self) -> str:
        """Stalker lifecycle pattern."""
        return "ephemeral"  # spawn → review → approve|reject → die
    
    async def review(self, work_report: str, file_paths: list = None) -> str:
        """Review Zealot work through information asymmetry protocol."""
        print(f"🛡️ {self.id} reviewing work: {work_report[:50]}...")
        
        # Information asymmetry strategy - review report vs code separately
        report_assessment = await self._review_report(work_report)
        
        if file_paths:
            code_assessment = await self._review_code(file_paths)
        else:
            code_assessment = "No code files provided for review"
        
        # Binary decision through 5 Quality Gates
        decision = await self._apply_quality_gates(work_report, report_assessment, code_assessment)
        
        return decision
    
    async def _review_report(self, work_report: str) -> str:
        """Review work report for intent and logic gaps."""
        prompt = f"""
STALKER REPORT REVIEW - Information Asymmetry Phase 1

Work Report: {work_report}

REVIEW FOCUS:
- Intent vs requirements alignment
- Logic gaps and assumptions  
- Scope completeness
- Claims verification

Return detailed assessment of what this report claims was accomplished.
"""
        
        result = ""
        async for event in self.agent.stream(prompt, conversation_id=f"{self.id}-report"):
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        return result or "Report review completed"
    
    async def _review_code(self, file_paths: list) -> str:
        """Review actual code implementation for quality and vulnerabilities."""
        prompt = f"""
STALKER CODE REVIEW - Information Asymmetry Phase 2

Files to review: {file_paths}

REVIEW FOCUS:
- Implementation bugs and security holes
- Bad patterns and architectural violations
- Performance issues and scalability problems
- Code quality and maintainability

Use FileRead to examine the actual code. Return detailed technical assessment.
"""
        
        result = ""
        async for event in self.agent.stream(prompt, conversation_id=f"{self.id}-code"):
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        return result or "Code review completed"
    
    async def _apply_quality_gates(self, work_report: str, report_assessment: str, code_assessment: str) -> str:
        """Apply 5 Quality Gates for binary approval/rejection."""
        prompt = f"""
STALKER QUALITY GATES - Binary Decision Required

Work Report: {work_report}
Report Assessment: {report_assessment}
Code Assessment: {code_assessment}

Apply ALL 5 Quality Gates:
1. **Reference Grade** - Is this exemplary work?
2. **Canonical** - Is this THE definitive way?
3. **Beauty** - Does this add ceremony or reduce it?
4. **Regret Test** - Will we fucking regret this in 6 months?
5. **Extensibility** - Can this grow cleanly without breaking?

DEFAULT: NO. Prove quality deserves YES.

Return either:
- **APPROVED** - All 5 gates passed, with brief reasoning
- **REJECTED** - Gate failure detected, with surgical feedback on exact issues

Quality standards never slip.
"""
        
        result = ""
        async for event in self.agent.stream(prompt, conversation_id=f"{self.id}-gates"):
            if event.get("type") == "respond":
                result = event.get("content", "")
                break
        
        # Ensure binary outcome
        if result and ("APPROVED" in result.upper() or "REJECTED" in result.upper()):
            return result
        else:
            return f"**REJECTED** - Quality gate assessment failed to provide binary decision"
    
    async def escalate_architectural_conflict(self, conflict_details: str) -> str:
        """Escalate architectural conflicts to Sacred Four for constitutional guidance."""
        from ..conclave import Conclave
        
        try:
            conclave = Conclave()
            
            question = f"""STALKER ARCHITECTURAL ESCALATION: {conflict_details}
            
Stalker {self.id} detected architectural conflict requiring constitutional guidance.
Standards enforcement vs implementation requirements conflict detected."""
            
            print(f"🛡️ {self.id} escalating architectural conflict to Sacred Four")
            guidance = await conclave.convene(question)
            
            return f"""SACRED FOUR ARCHITECTURAL GUIDANCE

Stalker: {self.id}
Conflict: {conflict_details}
Status: Constitutional guidance provided

{guidance}"""
            
        except Exception as e:
            return f"""ESCALATION FAILED: {e}
            
Stalker: {self.id}
Conflict: {conflict_details}
Status: Sacred Four coordination unavailable

Enforcing quality standards despite escalation failure."""