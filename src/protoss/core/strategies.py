"""Agent selection strategies for Engine orchestration."""

from typing import List, Tuple


class AgentStrategy:
    """Base class for agent selection strategies."""

    def select_agents(self, task: str, requested_count: int) -> List[Tuple[str, str]]:
        """Select appropriate agents for the given task.

        Returns:
            List of (agent_name, agent_type) tuples
        """
        raise NotImplementedError


class StandardStrategy(AgentStrategy):
    """Standard agent selection for most coordination tasks."""

    def select_agents(self, task: str, requested_count: int) -> List[Tuple[str, str]]:
        """Select agent types for coordination - returns specs not instances."""
        agents = []

        # Always start with executor
        agents.append(("executor", "Executor"))

        # Add zealots for parallel work
        zealot_count = min(requested_count - 1, 3)  # Cap zealots for sanity
        for i in range(zealot_count):
            agents.append((f"zealot-{i+1}", "Zealot"))

        # Add constitutional deliberation for complex decisions
        if self._needs_constitutional_review(task):
            agents.append(("conclave", "Conclave"))

        return agents

    def _needs_constitutional_review(self, task: str) -> bool:
        """Determine if task requires constitutional deliberation."""
        architecture_keywords = ["architecture", "design", "approach", "strategy"]
        return any(keyword in task.lower() for keyword in architecture_keywords)


class MinimalStrategy(AgentStrategy):
    """Minimal agent selection for simple tasks."""

    def select_agents(self, task: str, requested_count: int) -> List[Tuple[str, str]]:
        """Select only executor for simple coordination."""
        return [("executor", "Executor")]


class ResearchStrategy(AgentStrategy):
    """Research-focused agent selection."""

    def select_agents(self, task: str, requested_count: int) -> List[Tuple[str, str]]:
        """Select archon + conclave for knowledge-heavy tasks."""
        agents = []

        # Start with archon for context
        agents.append(("archon", "Archon"))

        # Add conclave for analysis
        agents.append(("conclave", "Conclave"))

        # Add executor for coordination
        agents.append(("executor", "Executor"))

        return agents


def get_strategy(task: str, config) -> AgentStrategy:
    """Select appropriate strategy based on task characteristics."""
    task_lower = task.lower()

    # Research tasks
    if any(
        word in task_lower for word in ["research", "analyze", "investigate", "study"]
    ):
        return ResearchStrategy()

    # Simple tasks
    if (
        any(word in task_lower for word in ["fix", "update", "change", "modify"])
        and len(task.split()) < 8
    ):
        return MinimalStrategy()

    # Default to standard strategy
    return StandardStrategy()
