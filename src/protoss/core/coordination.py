"""Coordination utilities for message parsing and context flattening."""

import logging
from typing import List
from dataclasses import dataclass
from .config import Config
from .bus import Message

logger = logging.getLogger(__name__)


@dataclass
class Signals:
    """Parsed completion signals from agent responses."""

    complete: bool = False
    escalate: bool = False


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

## COMPLETION SIGNALS
Use these signals to indicate task status:
- [COMPLETE] - Task is fully finished and ready
- [ESCALATE] - Need constitutional guidance on complex decisions

## COORDINATION PROTOCOL
- Review any team messages for context and coordination
- Work naturally with other agents through discussion
- Report progress clearly for team awareness
- Use completion signals when appropriate

Focus on beautiful, simple solutions. Push back on complexity.
"""


def flatten(messages: List[Message], config: Config) -> str:
    """Convert channel messages to flattened context for agent execution.

    Args:
        messages: List of channel messages
        config: Configuration for context limits

    Returns:
        Flattened context string for agent consumption
    """
    if not messages:
        return "You are the first agent working on this task."

    # Limit to recent messages based on config
    recent_messages = messages[-config.max_context :]

    formatted = []
    for msg in recent_messages:
        formatted.append(f"{msg.sender}: {msg.content}")

    return "\n".join(formatted)


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

    if config.escalate.upper() in response_upper:
        signals.escalate = True

    return signals


async def consult(question: str) -> str:
    """Request strategic consultation from Conclave.

    Args:
        question: Question or issue requiring constitutional guidance

    Returns:
        Strategic guidance from constitutional consultation
    """
    # TODO: Implement actual Conclave consultation
    logger.info(f"Constitutional consultation requested: {question[:100]}...")
    return f"Strategic guidance on: {question} - [Implementation pending]"
