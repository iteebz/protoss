"""Coordination utilities for message parsing and context flattening."""

import logging
from typing import List
from dataclasses import dataclass
from .config import Config
from .message import Message

logger = logging.getLogger(__name__)


@dataclass
class Signals:
    """Parsed completion signals from agent responses."""

    complete: bool = False
    despawn: bool = False


def instructions(identity: str, task: str) -> str:
    """Build coordination instructions layered with constitutional identity.

    Args:
        identity: Constitutional identity for the agent
        task: The coordination task

    Returns:
        Complete instruction set for agent execution
    """
    return f"""{identity}

## COORDINATION TASK
{task}

## COORDINATION SIGNALS
Use these patterns for natural coordination:
- @arbiter - Human escalation or completion reporting
- @archon - Context/memory needs (auto-summarizes on completion)  
- @conclave - Constitutional guidance on complex decisions
- !despawn - Agent finished, remove self

## COORDINATION PROTOCOL
- Review any team messages for context and coordination
- Work naturally with other agents through discussion
- Report progress clearly for team awareness
- Use completion signals when appropriate

Focus on beautiful, simple solutions. Push back on complexity.
"""


def flatten(messages: List[Message], config: Config, agent_type: str = None) -> str:
    """Convert channel messages to flattened context for agent execution.

    Args:
        messages: List of channel messages
        config: Configuration for context limits
        agent_type: Agent type for context filtering (archon gets full stream)

    Returns:
        Flattened context string for agent consumption
    """
    if not messages:
        return "You are the first agent working on this task."

    # Limit to recent messages based on config
    recent_messages = messages[-config.max_context :]

    # Agent-specific filtering
    if agent_type == "archon":
        # Archon sees full event stream for compression/archival
        filtered_messages = recent_messages
    else:
        # Other agents see only respond events for clean coordination
        filtered_messages = []
        for msg in recent_messages:
            # Filter out tool events [THINK] [CALL] [RESULT] but keep responds and system
            if not msg.content.startswith(("[THINK]", "[CALL]", "[RESULT]")):
                filtered_messages.append(msg)

    formatted = []
    for msg in filtered_messages:
        formatted.append(f"{msg.sender}: {msg.content}")

    return (
        "\n".join(formatted)
        if formatted
        else "You are the first agent working on this task."
    )


def parse(response: str, config: Config) -> Signals:
    """Parse agent response for completion signals.

    Args:
        response: Agent response text
        config: Configuration with signal definitions

    Returns:
        Parsed signals indicating completion or escalation
    """
    signals = Signals()

    response_upper = response.upper()

    if config.complete.upper() in response_upper:
        signals.complete = True

    if "!DESPAWN" in response_upper:
        signals.despawn = True

    return signals


# consult() function removed - agents use natural @conclave mentions for constitutional consultation
# No orchestration needed - pure emergent coordination through conversation
