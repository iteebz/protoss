"""Coordination: Core coordination functions.

Clean abstractions for multi-agent coordination through conversation.
"""

from typing import List, Optional, Protocol
from dataclasses import dataclass
from .config import get_config


class PathwayMessage(Protocol):
    """Protocol for pathway message objects."""
    sender: str
    content: str


@dataclass
class CompletionSignal:
    """Parsed completion signals from agent responses."""
    complete: bool = False
    escalate: bool = False
    continue_work: bool = True


def flatten(messages: List[PathwayMessage], max_context: Optional[int] = None) -> str:
    """Convert pathway messages to single user message for agent context.
    
    Args:
        messages: List of pathway messages from khala.attune()
        max_context: Maximum number of recent messages to include (uses config default if None)
        
    Returns:
        Flattened string suitable for agent execution
        
    Raises:
        ValueError: If max_context is less than 1
    """
    config = get_config()
    if max_context is None:
        max_context = config.max_context
    
    if max_context < 1:
        raise ValueError("max_context must be at least 1")
        
    if not messages:
        return "You are the first agent working on this task."
    
    # Window recent context to prevent explosion
    recent = messages[-max_context:] if len(messages) > max_context else messages
    
    # Format for natural conversation context
    formatted = []
    for msg in recent:
        if not msg.sender or not hasattr(msg, 'content'):
            continue  # Skip malformed messages
        formatted.append(f"{msg.sender}: {msg.content}")
    
    return "\n".join(formatted) if formatted else "No valid messages in pathway context."


def parse(response: str) -> CompletionSignal:
    """Parse completion signals from agent response.
    
    Args:
        response: Agent response text
        
    Returns:
        CompletionSignal with parsed flags
        
    Raises:
        ValueError: If response is None or empty
    """
    if not response:
        raise ValueError("Response cannot be None or empty")
    
    config = get_config()
    complete = config.complete in response
    escalate = config.escalate in response
    
    return CompletionSignal(
        complete=complete,
        escalate=escalate,
        continue_work=not (complete or escalate)
    )


def instructions(
    constitutional_identity: str,
    task: str, 
    pathway_members: Optional[List[str]] = None,
    pathway_history: Optional[str] = None
) -> str:
    """Build layered instructions: constitution + coordination context."""
    if not constitutional_identity:
        raise ValueError("Constitutional identity cannot be empty")
    if not task:
        raise ValueError("Task cannot be empty")
    
    # Team awareness
    if pathway_members and len(pathway_members) > 0:
        team_context = f"Your team: {', '.join(str(member) for member in pathway_members)}"
    else:
        team_context = "Your team: Will be discovered through coordination"
    
    # Context awareness  
    if pathway_history and pathway_history.strip():
        context_section = f"Recent context: {pathway_history.strip()}"
    else:
        context_section = "Recent context: You are starting fresh"
    
    coordination_layer = f"""
## COORDINATION CONTEXT
You are working with fellow agents on: {task}

{team_context}
{context_section}

## COORDINATION WORKFLOW  
- Discuss approach and divide work naturally
- Implement your piece applying constitutional standards
- Request review when ready
- Review teammates' work with constitutional rigor
- Reach collective agreement

When the whole task is done: [COMPLETE]
If stuck and need help: [ESCALATE]

Choose what to work on based on team discussion.
Apply constitutional principles to coordination - push back on overengineering, defend simplicity.
"""

    return f"{constitutional_identity}\n\n{coordination_layer}"